from typing import Any
from typing import Dict

from bs4 import BeautifulSoup


def parse_form(*, form) -> Dict[str, Any]:
    inputs = {
        element["name"]: element["value"]
        for element in form.find_all("input")
        if element.get("type") != "submit"
    }
    for element in form.find_all("select"):
        inputs[element["name"]] = element.find("option", {"selected": True})["value"]
    return inputs


def load_admin_form(*, client, instance):
    model_name = instance.__class__.__name__.lower()
    url = f"/admin/demo/{model_name}/{instance.pk}/change/"
    response = client.get(url)
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    form = soup.find("form", {"id": f"{model_name}_form"})
    inputs = parse_form(form=form)
    return inputs


def get_errors(soup):
    return soup.find_all("div", {"class": "errors"}) or soup.find_all(
        "ul", {"class": "errorlist"}
    )


def save_admin_form(*, client, instance, inputs):
    args = dict(inputs)
    args["_save"] = "Save"
    model_name = instance.__class__.__name__.lower()
    url = f"/admin/demo/{model_name}/{instance.pk}/change/"
    return client.post(url, args)


def reloaded(instance):
    return instance.__class__.objects.get(pk=instance.pk)


# TODO: test that a form succeeds if a field is modified in the background
# which is not shown on the current form


def test_normal_modify(admin_client, freddy):
    new_note_value = "sdflkj the first"
    inputs = load_admin_form(client=admin_client, instance=freddy)
    inputs["notes"] = new_note_value
    response = save_admin_form(client=admin_client, instance=freddy, inputs=inputs)
    assert response.status_code == 302
    soup = BeautifulSoup(response.content, "html.parser")
    errors = get_errors(soup)
    assert not errors, errors
    assert reloaded(freddy).notes == new_note_value.title()


def test_conflicting_modify(admin_client, freddy):
    # two windows/tabs load the same record
    inputs1 = load_admin_form(client=admin_client, instance=freddy)
    inputs2 = load_admin_form(client=admin_client, instance=freddy)

    # they try to change a field to different values
    # (though the test would fail even if the values were the same)
    new_note_value1 = "sdflkj"
    new_note_value2 = "lkjdfljkfd"
    inputs1["notes"] = new_note_value1
    inputs2["notes"] = new_note_value2

    # the first one succeeds in saving the change
    response = save_admin_form(client=admin_client, instance=freddy, inputs=inputs1)
    assert response.status_code == 302
    soup = BeautifulSoup(response.content, "html.parser")
    errors = get_errors(soup)
    assert not errors, errors
    assert reloaded(freddy).notes == new_note_value1.title()

    # the second one fails and is shown an error
    response = save_admin_form(client=admin_client, instance=freddy, inputs=inputs2)
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    errors = get_errors(soup)
    assert errors
    assert "object has changed" in str(errors)
    assert reloaded(freddy).notes == new_note_value1.title()
