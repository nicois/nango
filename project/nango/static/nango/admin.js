/* eslint-disable no-unused-vars, quotes */

function nangoShowValidationError(inputId, validationErrors) {
  const div = document.createElement("div");
  const ul = document.createElement("ul");
  ul.classList.add("errorlist");
  const li = document.createElement("li");
  li.appendChild(document.createTextNode(`${validationErrors}`));
  ul.appendChild(li);
  div.appendChild(ul);
  div.dataset.messageForFormId = inputId;
  const input = document.getElementById(inputId);
  input.parentNode.insertBefore(div, input.nextSibling);
}
