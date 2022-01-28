from asyncio.exceptions import TimeoutError
from pprint import pprint
from typing import Dict

import pytest
from channels.testing import WebsocketCommunicator
from demo.models import Customer
from nango.common import serialise_model_attr
from nango.consumers import LiveUpdatesConsumer


async def register(*, communicator: WebsocketCommunicator, customer: Customer):
    fields = [
        {
            "appLabel": "demo",
            "model": "customer",
            "pk": str(customer.pk),
            "attr": attr,
            "id": f"id_foo-{attr}",
            "value": serialise_model_attr(customer, attr),
        }
        for attr in ["name", "notes", "company"]
    ]

    message = dict(action="Register", fields=fields)
    pprint(message)
    await communicator.send_json_to(message)


async def clean(
    *, communicator: WebsocketCommunicator, customer: Customer, original: Dict[str, str]
):
    pass


def serialise_to_dict(customer: Customer) -> Dict[str, str]:
    return {
        attr: serialise_model_attr(customer, attr)
        for attr in ["name", "notes", "company"]
    }


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_modify(freddy: Customer):
    """
    Pretty boring: register the model,
    don't expect anything back
    """
    communicator = WebsocketCommunicator(
        LiveUpdatesConsumer.as_asgi(), "/ws/liveupdates/"
    )
    connected, subprotocol = await communicator.connect()
    assert connected
    await register(communicator=communicator, customer=freddy)
    with pytest.raises(TimeoutError):
        await communicator.receive_from()
    # Close
    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_clean_name(freddy: Customer):
    raw_name = "roger ramjet"
    communicator = WebsocketCommunicator(
        LiveUpdatesConsumer.as_asgi(), "/ws/liveupdates/"
    )
    connected, subprotocol = await communicator.connect()
    assert connected
    await register(communicator=communicator, customer=freddy)
    original = serialise_to_dict(freddy)
    freddy.name = raw_name
    await clean(communicator=communicator, customer=freddy, original=original)
    with pytest.raises(TimeoutError):
        response = await communicator.receive_json_from()
        pprint(response)
    # Close
    await communicator.disconnect()
