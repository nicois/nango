import json
import logging
from collections import defaultdict
from typing import Any
from typing import Dict
from typing import Set
from typing import Tuple

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.apps import apps

from .common import decode_pk
from .common import instance_ref_to_channel_group_key
from .common import serialise_value

LOGGER = logging.getLogger(__file__)

MessageType = Tuple[str, str, Any]


class LiveUpdatesConsumer(AsyncWebsocketConsumer):  # type: ignore
    def __init__(self, **kw):
        super().__init__(**kw)
        self._my_groups: Set[str] = set()
        self.fields_for_instance: Dict[MessageType, Dict[str, Any]] = defaultdict(dict)

    async def connect(self) -> None:
        await self.accept()

    def _retrieve_instance_values(self, app, model, pk, attrs):
        Model = apps.get_model(app, model)
        instance = Model.objects.get(pk=pk)
        return {attr: getattr(instance, attr) for attr in attrs}

    async def saved(self, info) -> None:
        message = info["message"]
        app = message["app"]
        model = message["model"]
        pkey = message["pk"]
        fields = self.fields_for_instance[(app, model, pkey)]
        instance = await sync_to_async(self._retrieve_instance_values)(
            app=app, model=model, pk=pkey, attrs=fields
        )
        for attr, original_value in fields.items():
            new_value = serialise_value(value=instance[attr])
            if original_value != new_value:
                message = dict(
                    message=dict(
                        app=app,
                        model=model,
                        pk=pkey,
                        attr=attr,
                        original_value=original_value,
                        new_value=new_value,
                    )
                )
                await self.send(text_data=json.dumps(message))
                fields[attr] = new_value

    async def receive(self, text_data: bytes) -> None:
        text_data_json = json.loads(text_data)
        for instance_ref in text_data_json["register"]:
            app_label = instance_ref["appLabel"]
            model = instance_ref["model"]
            pkey = decode_pk(instance_ref["pk"])
            group_key = instance_ref_to_channel_group_key(
                app_label=app_label, model=model, pk=pkey
            )
            fields = self.fields_for_instance[(app_label, model, pkey)]
            fields[instance_ref["attr"]] = instance_ref["value"]
            self._my_groups.add(group_key)

        for group_key in self._my_groups:
            await self.channel_layer.group_add(
                channel=self.channel_name, group=group_key
            )
            await self.saved(
                info=dict(message=dict(app=app_label, model=model, pk=pkey))
            )

    async def disconnect(self, close_code: Any) -> None:
        for my_group in self._my_groups:
            await self.channel_layer.group_discard(
                group=my_group, channel=self.channel_name
            )
