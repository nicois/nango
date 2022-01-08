import json
import logging
from types import MethodType
from typing import Any

from django.conf import settings
from django.db.models import Model
from django.utils.html import format_html

DELIMITER = "."
LOGGER = logging.getLogger(__file__)


def encode_pk(pk: Any) -> str:
    return json.dumps(pk)


def decode_pk(encoded_pk: str) -> Any:
    return json.loads(encoded_pk)


def instance_ref_to_channel_group_key(app_label: str, model: str, pk: Any) -> str:
    return ".".join([app_label, model, str(pk)])


def serialise_model_attr(instance: Model, attr: str) -> str:
    """
    Returns a string representation of the value of
    this instance.
    """
    value = getattr(instance, attr)
    return serialise_value(value=value)


def serialise_value(*, value: Any) -> str:
    """
    Returns a string representation of the value of
    this instance.
    """
    if isinstance(value, Model):
        return str(value.pk)
    return str(value)


def set_original_form_values_on_instance(form, *, instance=None):
    """
    If the form has fields, look for the special __original-*
    fields. If provided, attach them to the associated instance,
    so they are respected when clean() is invoked
    """
    if not getattr(form, "fields", None):
        # form does not (yet) have fields, so nothing to do
        return

    for field_name, field in form.fields.items():
        field_key = (
            f"__original-{form.prefix}-{field_name}"
            if form.prefix
            else f"__original-{field_name}"
        )
        if field_key in form.data:
            original_value = form.data[field_key]
            try:
                (instance or form.instance)._original_form_values[
                    field_name
                ] = original_value
            except AttributeError:
                model = (instance or form.instance).__class__
                LOGGER.error(f"Model {model} is missing the nango mixin.")
                raise


def patch_widgets(form):
    """
    Modify the widgets so they will display the hidden inputs alongside
    the normal stuff.
    """
    websocket_connection_delay = getattr(
        settings, "NANGO_WEBSOCKET_CONNECTION_DELAY", -1
    )
    assert hasattr(form, "fields")
    for field_name, field in form.fields.items():
        widget = field.widget

        def _render(
            self,
            template,
            context,
            *args,
            _original_render=widget._render,
            _field_name=field_name,
            **kw,
        ):
            result = _original_render(template, context, *args, **kw)
            if "widget" not in context:
                return result

            hidden = format_html(
                f"""<input data-app-label="{form.instance._meta.app_label}"
                               data-model-name="{form.instance._meta.model_name}"
                               data-instance-pk="{encode_pk(form.instance.pk)}"
                               data-original-name="{{}}"
                               data-related-form-id="{{}}"
                               type="hidden"
                               data-connection-delay="{websocket_connection_delay}"
                               name="__original-{{}}"
                               value="{{}}">""",
                _field_name,
                context["widget"]["attrs"]["id"],
                context["widget"]["name"],
                serialise_model_attr(form.instance, _field_name),
            )
            return result + hidden

        widget._render = MethodType(_render, widget)
