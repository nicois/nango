import logging

from django.urls import re_path

from . import consumers
from .common import ENABLE_WEBSOCKET

LOGGER = logging.getLogger(__file__)

websocket_urlpatterns = []

if ENABLE_WEBSOCKET:
    websocket_urlpatterns.append(
        re_path(r"ws/liveupdates/$", consumers.LiveUpdatesConsumer.as_asgi())
    )
else:
    LOGGER.debug("Nango websockets are disabled")
