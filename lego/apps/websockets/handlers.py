from lego.apps.events.websockets import find_event_groups
from lego.apps.websockets.auth import jwt_create_channel_session, jwt_retrieve_channel_session

# TODO: Find this in all apps, automagically:
# find_methods contain functions used to detect what
# channels groups a user might belong to:
find_methods = [
    find_event_groups
]


def find_groups(user):
    groups = []
    for find in find_methods:
        groups += find(user)

    return groups


@jwt_create_channel_session
def handle_connect(message):
    groups = find_groups(message.user)
    for group in groups:
        group.add(message.reply_channel)


@jwt_retrieve_channel_session
def handle_disconnect(message):
    groups = find_groups(message.user)
    for group in groups:
        group.discard(message.reply_channel)
