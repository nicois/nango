from django import forms
from django.contrib import admin
from nango import forms
from nango.common import set_original_form_values_on_instance


class AdminMixin:
    def save_model(self, request, obj, form, change):
        set_original_form_values_on_instance(form=form, instance=obj)
        return super().save_model(request=request, obj=obj, form=form, change=change)


class ModelAdmin(AdminMixin, admin.ModelAdmin):
    form = forms.ModelForm
