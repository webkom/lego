from asgiref.sync import AsyncToSync
from channels.layers import get_channel_layer
from djangorestframework_camel_case.render import camelize

from lego.utils.json import serialize


def notify_group(group: str, message: dict):
    """
    Dumps the message to JSON and sends it to the specified channel.

    :param group: str
    :param message: dict
    """
    channel_layer = get_channel_layer()
    payload = serialize(camelize(message))
    return AsyncToSync(channel_layer.group_send)(
        group, {"type": "notification.message", "text": payload}
    )
