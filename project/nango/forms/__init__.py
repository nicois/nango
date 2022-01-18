import logging
from functools import partial
from inspect import isclass
from inspect import signature
from types import MethodType
from typing import Any
from typing import cast
from typing import Dict
from typing import Optional
from typing import Set

from django import forms
from django.conf import settings
from django.db.models import Model
from django.utils.html import format_html

from ..common import ENABLE_WEBSOCKET
from ..common import encode_pk
from ..common import serialise_model_attr

Fields = Set[str]

DEFAULT_DEBOUNCE_PERIOD: float = getattr(settings, "DEFAULT_DEBOUNCE_PERIOD", 0.2)

LOGGER = logging.getLogger(__file__)


class FormMixin:
    auto_clean_debounce_period: float = DEFAULT_DEBOUNCE_PERIOD
    auto_submit_debounce_period: float = DEFAULT_DEBOUNCE_PERIOD

    auto_clean_fields: Optional[Fields] = None
    auto_submit_fields: Optional[Fields] = None

    def __init__(self, *args: Any, **kw: Any) -> None:
        super().__init__(*args, **kw)
        if hasattr(self, "fields"):
            patch_widgets(form=cast("Form", self))

    def clean(self, *args: Any, **kw: Any) -> Any:
        set_original_form_values_on_instance(form=cast("Form", self))
        return super().clean(*args, **kw)  # type: ignore


class ModelForm(FormMixin, forms.ModelForm):  # type: ignore
    pass


class Form(FormMixin, forms.Form):
    pass


def set_original_form_values_on_instance(
    form: Form, *, instance: Optional[Model] = None
):
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
                (instance or form.instance)._original_form_values[  # type: ignore
                    field_name
                ] = original_value
            except AttributeError:
                model = (instance or form.instance).__class__  # type: ignore
                LOGGER.error(f"Model {model} is missing the nango mixin.")
                raise


def patch_widgets(form: Form) -> None:
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
            attrs: Dict[str, str] = {
                "data-app-label": form.instance._meta.app_label,
                "data-model-name": form.instance._meta.model_name,
                "data-instance-pk": encode_pk(form.instance.pk),
                "data-original-name": _field_name,
                "data-related-form-id": context["widget"]["attrs"]["id"],
                "type": "hidden",
                "name": "__original-" + context["widget"]["name"],
                "value": serialise_model_attr(form.instance, _field_name),
            }

            if ENABLE_WEBSOCKET:
                attrs["data-connection-delay"] = str(websocket_connection_delay)

                if _field_name in (form.auto_submit_fields or {}):
                    attrs["data-auto-submit-debounce-period"] = str(
                        getattr(
                            form, "auto_submit_debounce_period", DEFAULT_DEBOUNCE_PERIOD
                        )
                        * 1000
                    )

                if _field_name in (form.auto_clean_fields or {}):
                    form.auto_clean_fields
                    attrs["data-auto-clean-debounce-period"] = str(
                        getattr(
                            form, "auto_clean_debounce_period", DEFAULT_DEBOUNCE_PERIOD
                        )
                        * 1000
                    )

            hidden = format_html(
                "<input "
                + "\n\t".join(f"{attr}={value}" for attr, value in attrs.items())
                + ">"
            )
            return result + hidden

        widget._render = MethodType(_render, widget)


def __getattr__(name: str) -> Any:
    original = getattr(forms, name)
    if isclass(original):
        # Anything derived from django's ModelForm gets
        # modified to have FormMixin too
        if issubclass(original, forms.Form) and not issubclass(original, FormMixin):

            return type(original.__name__, (FormMixin, original), {})
        return original

    if callable(original):
        sig = signature(original)
        # Anything with a 'form' argument which is derived from
        # django's ModelForm gets modified to have FormMixin too
        if form := sig.parameters.get("form"):
            default = form.default
            if issubclass(default, forms.Form) and not issubclass(default, FormMixin):
                return partial(
                    original, form=type(original.__name__, (FormMixin, default), {})
                )
        return original
    raise AttributeError(f"module {__name__} has no attribute {name}")
