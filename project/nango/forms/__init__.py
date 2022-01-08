from functools import partial
from inspect import isclass
from inspect import signature
from typing import Any

from django import forms
from nango.common import patch_widgets
from nango.common import set_original_form_values_on_instance


class FormMixin:
    def __init__(self, *args, **kw) -> None:
        super().__init__(*args, **kw)
        if fields := getattr(self, "fields", None):
            patch_widgets(form=self)

    def clean(self, *args, **kw):
        set_original_form_values_on_instance(form=self)
        return super().clean(*args, **kw)


class ModelForm(FormMixin, forms.ModelForm):
    pass


class Form(FormMixin, forms.Form):
    pass


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

                class NewForm(FormMixin, default):  # type: ignore
                    pass

                return partial(
                    original, form=type(original.__name__, (FormMixin, default), {})
                )
        return original
    raise AttributeError(f"module {__name__} has no attribute {name}")
