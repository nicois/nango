from inspect import isclass
from typing import Any

from django import forms
from django.contrib import admin
from nango import forms

from . import site  # noqa
from .admin import *  # noqa


def __getattr__(name: str) -> Any:
    OriginalClass = getattr(admin, name)
    if not isclass(OriginalClass):
        raise AttributeError(f"module {__name__} has no attribute {name}")

    """
    if issubclass(OriginalClass, forms.ModelForm):

        class NewForm(forms.FormMixin, OriginalClass):  # type: ignore
            pass

        return NewForm
    """

    if Form := getattr(OriginalClass, "form", None):
        Form = OriginalClass.form
        if not issubclass(Form, forms.FormMixin):

            class NewForm(forms.FormMixin, Form):  # type: ignore
                pass

            Form = NewForm

        class NewAdmin(AdminMixin, OriginalClass):  # type: ignore
            form = Form

        return NewAdmin

    # no form attribute, so leave as-is
    return OriginalClass


def register(*args, **kw):
    """
    You can use this in place of admin.site.register
    with your nango-aware models
    """
    return admin.register(*args, **kw)
