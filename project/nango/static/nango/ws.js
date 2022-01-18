/* eslint-disable no-unused-vars, quotes */

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
      `input[data-auto-${action.toLowerCase()}-debounce-period]`
    );
    if (elements.length === 0) return; // nothing to do
    elements.forEach(element => {
      const visibleInput = document.getElementById(
        element.dataset.relatedFormId
      );
      const debouncePeriodMs = parseInt(
        element.dataset[`auto${action}DebouncePeriod`],
        10
      );
      visibleInput.addEventListener(
        "input",
        debounce(() => {
          const currentInput = document.getElementById(
            element.dataset.relatedFormId
          );
          const currentValue = currentInput.value;
          ws.send(
            JSON.stringify({ action, dataset: element.dataset, currentValue })
          );
        }, debouncePeriodMs)
      );
    });
  });
}

function nangoDecideWhetherToReload(data, elements, changedFormElements) {
  /**
   * Given that upstream changes have occurred, what do we do?
   * If there are local changes to inputs which overlap with the
   * upstream changes, the only safe thing to do is reload the page,
   * and start again.
   * However, if those inputs still have their original values, we
   * can just patch them in place and allow the user to continue.
   **/

  let message = `Since you began editing this form, the value of ${data.attr} has changed from ${data.original_value} to ${data.new_value}.`;
  if (changedFormElements.length > 0) {
    message = `${message}
You have already modified some of these. Select 'OK' to reload the page.`;
    if (window.confirm(message)) {
      window.location.reload();
    }
  } else {
    message = `${message}
You have not modified any of these form elements, so the values will be automatically updated.`;
    window.alert(message);
    // now update 'original_value' to the new values and
    // reset the current values back to the originals.
    elements.forEach(element => {
      const visibleInput = document.getElementById(
        element.dataset.relatedFormId
      );
      // TODO: we need to set the 'original value' to the new value too don't we?? Or was that done somewhere else already?
      nangoUnmarkInputAsOutdated(visibleInput);
      element.value = data.new_value;
      visibleInput.value = data.new_value;
    });
  }
}

function nangoOnSubmit(data) {
  console.log("submitted:");
  console.log(data);
}

function nangoOnClean(data) {
  /**
   * Process the results of a server-side clean operation
   **/
  const visibleInput = document.querySelector(`#${data.dataset.relatedFormId}`);
  const hiddenElement = document.querySelector(
    `input[data-related-form-id=${data.dataset.relatedFormId}]`
  );
  // abort if the current input value no longer matches what was submitted
  const currentValue = visibleInput.value;
  if (currentValue !== data.currentValue) {
    console.log(
      `Not updating field as ${data.dataset.originalName} is ${currentValue}, no longer ${data.currentValue}.`
    );
    return;
  }

  // remove any validation errors/states/classes relating to a prior 'clean' result,
  // which is now obsolete
  document
    .querySelectorAll(
      `[data-message-for-form-id=${data.dataset.relatedFormId}]`
    )
    .forEach(element => element.remove());

  if (data.cleanedValue) {
    // update the form input to show the cleaned value as returned from django
    visibleInput.value = data.cleanedValue;
    visibleInput.dataset.nangoState = "clean";
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

function nangoOnUpstreamChange(data) {
  /**
   * This is the handler for messages coming from the server
   **/
  //  app, attr, model, new_value, original_value, pk
  // Find form elements referencing this attribute.
  console.log(data);
  const elements = document.querySelectorAll(
    `input[data-app-label="${data.app}"][data-model-name="${data.model}"][data-instance-pk="${data.pk}"][data-original-name="${data.attr}"]`
  );
  // Work out whether any of them have changed.
  const changedFormElements = [];
  elements.forEach(element => {
    const visibleInput = document.getElementById(element.dataset.relatedFormId);
    const currentValue = visibleInput.value;
    if (currentValue !== element.value) {
      changedFormElements.push(element);
    }
    nangoMarkInputAsOutdated(visibleInput);
  });
  nangoDecideWhetherToReload(data, elements, changedFormElements);
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
            nangoOnUpstreamChange(data.message);
            break;
          case "submit":
            nangoOnSubmit(data.message);
            break;
          case "clean":
            nangoOnClean(data.message);
            break;
          default:
            console.error(`Unknown action in ${data}`);
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
        ws.send(JSON.stringify({ fields, action: "Register" }));
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
