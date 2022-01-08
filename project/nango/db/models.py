import logging
from inspect import isclass
from typing import Any
from typing import Dict
from typing import List

from asgiref.sync import async_to_sync

try:
    from channels.layers import get_channel_layer
except ModuleNotFoundError:
    get_channel_layer = None

from django.core.exceptions import ValidationError

from django.db import models
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from ..common import DELIMITER
from ..common import serialise_model_attr

LOGGER = logging.getLogger(__file__)


class TrackableMixin:
    """
    Support value tracking. Required for CAS-style validation on
    submission of a form, as well as realtime WS client updates
    """

    def __init__(self, *args, **kw) -> None:
        super().__init__(*args, **kw)
        self._original_form_values: Dict[str, Any] = dict()

    class Meta:
        abstract = True

    def save(self, *args, **kw):
        result = super().save(*args, **kw)
        if get_channel_layer:
            channel_layer = get_channel_layer()
            model_identifier = DELIMITER.join(
                [self._meta.app_label, self._meta.model_name, str(self.pk)]
            )
            message = dict(
                type="saved",
                message=dict(
                    app=self._meta.app_label, model=self._meta.model_name, pk=self.pk
                ),
            )

            def on_commit() -> None:
                async_to_sync(channel_layer.group_send)(model_identifier, message)

            transaction.on_commit(on_commit)
        return result

    def clean(self, *args, **kw):
        # If there is no pkey yet, this is a new object, so can't conflict
        if self._original_form_values and self.pk:
            errors: List[ValidationError] = []
            copy = self.__class__.objects.select_for_update().get(pk=self.pk)
            for attr, expected_value in self._original_form_values.items():
                current_stored_value = serialise_model_attr(copy, attr)
                if current_stored_value != expected_value:
                    errors.append(
                        ValidationError(
                            _(
                                "Field %(attr)s was %(original)s when you started editing it, but is %(db)s in the database."
                            ),
                            params=dict(
                                attr=attr,
                                original=expected_value,
                                db=current_stored_value,
                            ),
                        )
                    )
            if errors:
                raise ValidationError(
                    [
                        ValidationError(
                            _(
                                "This object has changed while you were editing it. "
                                "You will need to reload this page and make your changes again, "
                                "if they are still appropriate."
                            )
                        )
                    ]
                    + errors
                )
        super().clean(*args, **kw)


class LockableMixin:
    """
    Support instance locking. Allows views to identify the instance
    as locked, preventing others from modifying it
    (buildout: optional per-field granularity)
    """

    class Meta:
        abstract = True


class Model(TrackableMixin, models.Model):
    class Meta:
        abstract = True


def __getattr__(name: str) -> Any:
    original = getattr(models, name)
    if isclass(original):
        if issubclass(original, models.Model) and not issubclass(
            original, TrackableMixin
        ):
            return type(original.__name__, (TrackableMixin, original), {})
    return original

    # raise AttributeError(f"module {__name__} has no attribute {name}")
