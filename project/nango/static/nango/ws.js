/* eslint-disable no-unused-vars, quotes */

function uuidv4() {
  return ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, c =>
    (
      c ^
      (crypto.getRandomValues(new Uint8Array(1))[0] & (15 >> (c / 4)))
    ).toString(16)
  );
}

const nangoTabId = uuidv4();

const debounce = (callback, wait) => {
  let timeoutId = null;
  return (...args) => {
    window.clearTimeout(timeoutId);
    timeoutId = window.setTimeout(() => {
      callback.apply(null, args);
    }, wait);
  };
};

function nangoUnmarkInputAsOutdated(element) {
  element.classList.remove("nango-outdated");
}
function nangoMarkInputAsOutdated(element) {
  element.classList.add("nango-outdated");
}

function setupDebounces(ws) {
  /**
   * Identify any inputs which we should be monitoring changes in,
   * either for cleaning or submitting, and set up the infra for
   * doing so
   **/
  // FIXME: what if an element has clean and submit???
  const actions = ["Clean", "Submit"];
  actions.forEach(action => {
    const elements = document.querySelectorAll(
      `input[data-auto-${action.toLowerCase()}-debounce-period-ms]`
    );
    if (elements.length === 0) return; // nothing to do
    elements.forEach(element => {
      const visibleInput = document.getElementById(
        element.dataset.relatedFormId
      );
      const debouncePeriodMs = parseInt(
        element.dataset[`auto${action}DebouncePeriodMs`],
        10
      );
      const debounced = debounce(() => {
        const currentInput = document.getElementById(
          element.dataset.relatedFormId
        );
        const currentValue = currentInput.value;
        const originalValue = element.value;
        ws.send(
          JSON.stringify({
            action,
            dataset: element.dataset,
            currentValue,
            originalValue,
            nangoTabId
          })
        );
      }, debouncePeriodMs);
      visibleInput.addEventListener("input", () => {
        visibleInput.dataset.nangoState = "unknown";
        debounced();
      });
    });
  });
}

function nangoDecideWhetherToReload(
  upstreamTabId,
  data,
  elements,
  changedFormElements
) {
  /**
   * Given that upstream changes have occurred, what do we do?
   * If there are local changes to inputs which overlap with the
   * upstream changes, the only safe thing to do is reload the page,
   * and start again.
   * However, if those inputs still have their original values, we
   * can just patch them in place and allow the user to continue.
   *
   * two complications:
   * - What if we make 2 changes to an autosave field before any feedback?
   *   The first feedback message will no longer match the 'original' value.
   *   We need to discard this message, as it is superseded.
   * - What if another session makes a change to an autosave field which was also locally changed?
   *   The simplest thing is to blow away the local change, replacing it with the upstream change.
   *
   *  Therefore we need to modify things to mean the WS messages include a unique tab ID. This can be
   *  reflected by the server to let us know if a change notification is related to what we have done.
   *  The logic should be:
   *    - if local value matches server's original value, update local value to align with server's value (as before)
   *    - otherwise
   *        - if change was due to me (ie: tab IDs match), discard it
   *        - otherwise, clobber the local change and maybe warn/reload the page
   **/

  let message = `Since you began editing this form, the value of ${data.attr} has changed from ${data.original_value} to ${data.new_value}.`;
  if (changedFormElements.length > 0 && upstreamTabId !== nangoTabId) {
    message = `${message}
You have already modified some of these. Select 'OK' to reload the page.`;
    if (window.confirm(message)) {
      window.location.reload();
    }
  } else {
    message = `${message}
You have not modified any of these form elements, so the values will be automatically updated.`;
    let showMessage = false;
    // now update 'original_value' to the new values and
    // reset the current values back to the originals.
    elements.forEach(element => {
      const visibleInput = document.getElementById(
        element.dataset.relatedFormId
      );
      /*
      // only enable the alert if this isn't an auto-submit field
      if (!element.dataset.autoSubmitDebouncePeriodMs) {
        console.log("showing message");
        console.log(element);
        showMessage = true;
      }
      */
      // TODO: we need to set the 'original value' to the new value too don't we?? Or was that done somewhere else already?
      nangoUnmarkInputAsOutdated(visibleInput);
      element.value = data.new_value;
      visibleInput.value = data.new_value;
    });
    if (showMessage) window.alert(message);
  }
}

function nangoOnClean(data) {
  /**
   * Process the results of a server-side clean operation.
   * Returns both the visible and hidden inputs if
   * the operation was successful.
   **/
  const visibleInput = document.querySelector(`#${data.dataset.relatedFormId}`);
  const hiddenElement = document.querySelector(
    `input[data-related-form-id=${data.dataset.relatedFormId}]`
  );
  const currentValue = visibleInput.value;
  // is the current input value no longer matches what was submitted?
  const inSync = currentValue === data.currentValue;

  // remove any validation errors/states/classes relating to a prior 'clean' result,
  // which is now obsolete
  document
    .querySelectorAll(
      `[data-message-for-form-id=${data.dataset.relatedFormId}]`
    )
    .forEach(element => element.remove());

  if (data.cleanedValue) {
    // update the form input to show the cleaned value as returned from django
    console.log(`updated vi.v to ${data.cleanedValue}`);
    if (inSync) {
      visibleInput.value = data.cleanedValue;
      visibleInput.dataset.nangoState = "clean";
    }
    return;
  }
  if (data.validationErrors) {
    visibleInput.dataset.nangoState = "dirty";
    nangoShowValidationError(data.dataset.relatedFormId, data.validationErrors);
  }
}

function nangoOnSubmit(data) {
  /**
   * Process the results of a server-side clean operation.
   * Returns both the visible and hidden inputs if
   * the operation was successful.
   **/
  if (data.error) {
    visibleInput.dataset.nangoState = "dirty";
    // nangoShowValidationError(data.dataset.relatedFormId, data.validationErrors);
    return;
  }
  const visibleInput = document.querySelector(`#${data.dataset.relatedFormId}`);
  const hiddenElement = document.querySelector(
    `input[data-related-form-id=${data.dataset.relatedFormId}]`
  );
  const currentValue = visibleInput.value;
  // is the current input value no longer matches what was submitted?
  const inSync = currentValue === data.currentValue;

  // remove any validation errors/states/classes relating to a prior 'clean' result,
  // which is now obsolete
  document
    .querySelectorAll(
      `[data-message-for-form-id=${data.dataset.relatedFormId}]`
    )
    .forEach(element => element.remove());

  if (data.cleanedValue) {
    // update the form input to show the cleaned value as returned from django
    console.log(`updated S vi.v to ${data.cleanedValue}`);
    hiddenElement.value = data.cleanedValue;
    if (inSync) {
      visibleInput.value = data.cleanedValue;
      visibleInput.dataset.nangoState = "saved";
    }
    return { visibleInput, hiddenElement };
  }
  // if there is a validation error relating to the wrong originalValue,
  // discard this error and induce another save event
  if (hiddenElement.value != data.originalValue) {
    const event = new Event("input", {
      bubbles: true,
      cancelable: true
    });
    visibleInput.dispatchEvent(event);
    return;
  }
  if (data.validationErrors) {
    visibleInput.dataset.nangoState = "dirty";
    nangoShowValidationError(data.dataset.relatedFormId, data.validationErrors);
  }
}

function nangoShowValidationError(inputId, validationErrors) {
  console.log(validationErrors);
  const span = document.createElement("div");
  span.classList.add("nango-validation-error");
  span.appendChild(document.createTextNode(`${validationErrors}`));
  span.dataset.messageForFormId = inputId;
  const input = document.getElementById(inputId);
  input.parentNode.insertBefore(span, input.nextSibling);
}

function nangoOnUpstreamChange(upstreamTabId, data) {
  /**
   * This is the handler for messages coming from the server
   **/
  //  app, attr, model, new_value, original_value, pk
  // Find form elements referencing this attribute.
  const elements = document.querySelectorAll(
    `input[data-app-label="${data.app}"][data-model-name="${data.model}"][data-instance-pk="${data.pk}"][data-original-name="${data.attr}"]`
  );
  // Work out whether any of them have changed.
  const changedFormElements = [];
  elements.forEach(element => {
    const visibleInput = document.getElementById(element.dataset.relatedFormId);
    const currentValue = visibleInput.value;
    if (currentValue !== element.value) {
      console.log(`"${currentValue}" !== "${element.value}"`);
      console.log(currentValue);
      console.log(element.value);
      changedFormElements.push(element);
    }
    nangoMarkInputAsOutdated(visibleInput);
  });
  nangoDecideWhetherToReload(
    upstreamTabId,
    data,
    elements,
    changedFormElements
  );
}

/**
 * Scan the current page, working out whether there are inputs
 * we should be monitoring via websocket
 **/
window.addEventListener("load", () => {
  const elements = document.querySelectorAll("input[data-related-form-id]");
  if (elements.length === 0) return; // nothing to do

  // -1 means to keep the websocket disabled
  const connectionDelay = parseInt(
    elements[0].dataset.connectionDelay || "-1",
    10
  );

  if (connectionDelay >= 0) {
    setTimeout(() => {
      const scheme =
        window.location.origin.split(":")[0] === "https" ? "wss" : "ws";
      const ws = new WebSocket(
        `${scheme}://${window.location.host}/ws/liveupdates/`
      );

      ws.onmessage = e => {
        const data = JSON.parse(e.data);
        switch (data.action) {
          case "modify":
            nangoOnUpstreamChange(data.nangoTabId, data.message);
            break;
          case "submit":
            nangoOnSubmit(data.message);
            break;
          case "clean":
            nangoOnClean(data.message);
            break;
          default:
            console.error(`Unknown action. Original message follows:`);
            console.error(data);
        }
        // document.querySelector("#chat-log").value += data.message + "\n";
      };

      ws.onclose = e => {
        console.error("Chat socket closed unexpectedly");
        // TODO: try to reopen?
      };

      // inform the server which model/attrs we care about, ensuring
      // we will be told when any of them change
      ws.onopen = e => {
        const fields = [];
        elements.forEach(element => {
          fields.push({
            appLabel: element.dataset.appLabel,
            model: element.dataset.modelName,
            pk: element.dataset.instancePk,
            attr: element.dataset.originalName,
            id: element.dataset.relatedFormId,
            value: element.value
          });
        });
        ws.send(JSON.stringify({ fields, nangoTabId, action: "Register" }));
      };
      // todo: add keepalives (ping/pong)?
      window.addEventListener("submit", () => {
        // if we don't do this we might get messages back during form submission,
        // which would not be helpful and may disrupt the flow
        ws.close();
      });
      setupDebounces(ws);
    }, 1000 * connectionDelay);
  }
});
