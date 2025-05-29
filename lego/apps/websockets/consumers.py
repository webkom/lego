from asgiref.sync import AsyncToSync
from channels.generic.websocket import JsonWebsocketConsumer

from lego.apps.events.websockets import find_event_groups
from lego.apps.websockets.groups import group_for_user, verify_group_access
from lego.apps.users.models import User
from lego.apps.websockets import constants

def find_groups(user: User):
    return ["global", group_for_user(user.pk)] + find_event_groups(user)


class GroupConsumer(JsonWebsocketConsumer):
    """
    Custom consumer for handling websocket groups.
    
    Create own logic for tracking user groups as the WebsocketConsumer groups functionality
    does not have access to the user object.
    """
    user_groups = set()
    user = None
    
    def debug(self, message):
        if self.user:
            print(f"[{self.user.username.upper()}] {message}")
        else:
            print(f"[NO USER IN SCOPE] {message}")
        
    def connect(self):
        user = self.scope["user"]
        for group in find_groups(user):
            AsyncToSync(self.channel_layer.group_add)(group, self.channel_name)
        self.user = user    
        self.user_groups = set(find_groups(user))
        self.accept()
        
    def disconnect(self, code):
        for group in self.user_groups:
            AsyncToSync(self.channel_layer.group_discard)(group, self.channel_name)
        self.user_groups.clear()
    
    def receive_json(self, content, **kwargs):
        type = content.get("type")
        payload = content.get("payload")
        
        if type == constants.WS_GROUP_JOIN_BEGIN:
            group = payload.get("group")
            if self.user and verify_group_access(self.user, group):
                AsyncToSync(self.channel_layer.group_add)(group, self.channel_name)
                self.user_groups.add(group)
                self.send_message(constants.WS_GROUP_JOIN_SUCCESS, payload={ "group": group })
            else:
                self.send_message(constants.WS_GROUP_JOIN_FAILURE, payload={ "group": group })
        
        if type == constants.WS_GROUP_LEAVE_BEGIN:
            group = payload.get("group")
            if group in self.groups:
                AsyncToSync(self.channel_layer.group_discard)(group, self.channel_name)
                self.user_groups.remove(group)
                self.send_message(constants.WS_GROUP_LEAVE_SUCCESS)
            
    
    def send_message(self, type: str, payload=None, meta=None): 
        """
        Send message on standardised format.
        """
        content = {
            "type": type,
            "payload": payload,
            "meta": meta
        }
        self.send_json(content)
    
    def notification_message(self, event):
        self.send(text_data=event["text"])
        
    

