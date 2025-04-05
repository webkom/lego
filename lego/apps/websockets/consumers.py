from asgiref.sync import AsyncToSync
from channels.generic.websocket import WebsocketConsumer

from lego.apps.events.websockets import find_event_groups
from lego.apps.users.models import User
from lego.apps.websockets.groups import group_for_user


def find_groups(user: User):
    return ["global", group_for_user(user.pk)] + find_event_groups(user)


class GroupConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        for group in find_groups(self.scope["user"]):
            AsyncToSync(self.channel_layer.group_add)(group, self.channel_name)

    def disconnect(self, message):
        for group in find_groups(self.scope["user"]):
            AsyncToSync(self.channel_layer.group_discard)(group, self.channel_name)

    def notification_message(self, event):
        self.send(text_data=event["text"])
