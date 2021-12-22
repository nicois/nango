from inspect import isclass
from typing import Any

from django import forms
from django.contrib import admin
from nango import forms
from nango.common import set_original_form_values_on_instance


class AdminMixin:
    def save_model(self, request, obj, form, change):
        set_original_form_values_on_instance(form=form, instance=obj)
        return super().save_model(request=request, obj=obj, form=form, change=change)


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

    Form = OriginalClass.form
    if not issubclass(Form, forms.FormMixin):

        class NewForm(forms.FormMixin, Form):  # type: ignore
            pass

        Form = NewForm

    class NewAdmin(AdminMixin, OriginalClass):  # type: ignore
        form = Form

    return NewAdmin


class ModelAdmin(AdminMixin, admin.ModelAdmin):
    form = forms.ModelForm


def register(model):
    """
    You can use this in place of admin.site.register
    with your nango-aware models
    """
    return admin.site.register(model, ModelAdmin)
