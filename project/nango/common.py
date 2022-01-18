import json
import logging
from typing import Any

from django.conf import settings
from django.db.models import Model

DELIMITER = "."
LOGGER = logging.getLogger(__file__)

ENABLE_WEBSOCKET: bool = getattr(settings, "NANGO_WEBSOCKET_CONNECTION_DELAY", -1) > -1


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
