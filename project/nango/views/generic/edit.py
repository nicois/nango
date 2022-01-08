from inspect import isclass
from types import MethodType
from typing import Any

from django.views.generic import edit
from nango.common import patch_widgets
from nango.common import set_original_form_values_on_instance
from nango.db.models import TrackableMixin

"""
idea: in the template, if certain fields are selected to be live-tracked,
then have as_p append the hidden fields (later on) and invoke the js code
to register the items.

as_p() uses 'django/forms/p.html' (or 'django/forms/forsets/p.html') to render with,
so we can simply shadow it.

For now, leave this file here as other tricks might require python changes
"""

"""
from django.db.models import get_model
mymodel = get_model('some_app', 'SomeModel')
"""


class Mixin:
    def get_form(self):
        form = super().get_form()
        if not isinstance(form.instance, TrackableMixin):
            return form

        patch_widgets(form)
        original_clean = form.clean

        def new_clean(self, *args, **kw):
            set_original_form_values_on_instance(form=self)
            return original_clean(*args, **kw)

        form.clean = MethodType(new_clean, form)

        return form


def __getattr__(name: str) -> Any:
    original_class = getattr(edit, name)
    if not isclass(original_class):
        raise AttributeError(f"module {__name__} has no attribute {name}")
    return type(
        original_class.__name__,
        (
            Mixin,
            original_class,
        ),
        {},
    )
