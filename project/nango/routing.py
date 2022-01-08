import logging

from django.conf import settings
from django.urls import re_path

from . import consumers

LOGGER = logging.getLogger(__file__)

websocket_urlpatterns = []

if getattr(settings, "NANGO_WEBSOCKET_CONNECTION_DELAY", -1) >= 0:
    websocket_urlpatterns.append(
        re_path(r"ws/liveupdates/$", consumers.LiveUpdatesConsumer.as_asgi())
    )
else:
    LOGGER.warning("Nango websockets are disabled as connection delay < 0")
