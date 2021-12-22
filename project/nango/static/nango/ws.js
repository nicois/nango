/* eslint-disable no-unused-vars, quotes */

function nangoUnmarkInputAsOutdated(element) {
  element.classList.remove("nango-outdated");
}
function nangoMarkInputAsOutdated(element) {
  element.classList.add("nango-outdated");
}

function nangoDecideWhetherToReload(data, elements, changedFormElements) {
  console.log(changedFormElements);

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
    elements.forEach((element) => {
      const visibleInput = document.getElementById(
        element.dataset.relatedFormId
      );
      nangoUnmarkInputAsOutdated(visibleInput);
      element.value = data.new_value;
      visibleInput.value = data.new_value;
    });
  }
}

function nangoOnUpstreamChange(data) {
  //  app, attr, model, new_value, original_value, pk
  // Find form elements referencing this attribute.
  console.log(data);
  const elements = document.querySelectorAll(
    `input[data-app-label="${data.app}"][data-model-name="${data.model}"][data-instance-pk="${data.pk}"][data-original-name="${data.attr}"]`
  );
  // Work out whether any of them have changed.
  const changedFormElements = [];
  elements.forEach((element) => {
    const visibleInput = document.getElementById(element.dataset.relatedFormId);
    const currentValue = visibleInput.value;
    if (currentValue !== element.value) {
      changedFormElements.push(element);
    }
    nangoMarkInputAsOutdated(visibleInput);
  });
  nangoDecideWhetherToReload(data, elements, changedFormElements);
}

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
      const ws = new WebSocket(`ws://${window.location.host}/ws/liveupdates/`);

      ws.onmessage = (e) => {
        const data = JSON.parse(e.data);
        console.log(data);
        nangoOnUpstreamChange(data.message);
        // document.querySelector("#chat-log").value += data.message + "\n";
      };

      ws.onclose = (e) => {
        console.error("Chat socket closed unexpectedly");
        // TODO: try to reopen?
      };

      ws.onopen = (e) => {
        const fields = [];
        elements.forEach((element) => {
          fields.push({
            appLabel: element.dataset.appLabel,
            model: element.dataset.modelName,
            pk: element.dataset.instancePk,
            attr: element.dataset.originalName,
            id: element.dataset.relatedFormId,
            value: element.value,
          });
        });
        ws.send(JSON.stringify({ register: fields }));
      };
      // remember the mapping
      // (todo)

      // todo: handle disconnects, add keepalives (ping/pong)
      window.addEventListener("submit", () => {
        ws.close();
      });
    }, 1000 * connectionDelay);
  }
});
