from django import forms
from django.contrib import admin
from nango import forms
from nango.common import ENABLE_WEBSOCKET


class AdminMixin:
    class Media:
        if ENABLE_WEBSOCKET:
            js = ["nango/ws.js", "nango/admin.js"]
            css = {"all": ["nango/ws.css"]}

    def save_model(self, request, obj, form, change):
        forms.set_original_form_values_on_instance(form=form, instance=obj)
        return super().save_model(request=request, obj=obj, form=form, change=change)

    def get_form(self, *args, **kw):
        form = super().get_form(*args, **kw)

        for attr in [
            "auto_clean_fields",
            "auto_submit_fields",
            "auto_clean_debounce_period",
            "auto_submit_debounce_period",
        ]:
            # Push this attr value from the generic
            # view to the form
            if attr_value := getattr(self, attr, None):
                setattr(form, attr, attr_value)

        return form


class ModelAdmin(AdminMixin, admin.ModelAdmin):
    form = forms.ModelForm
