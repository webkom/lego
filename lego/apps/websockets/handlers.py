from channels import Group

from lego.apps.websockets.auth import jwt_create_channel_session, jwt_retrieve_channel_session


def group_for_user(user):
    return Group(f'user-{user.pk}')


def group_for_event(event):
    return Group('event-{0}'.format(event.pk))


def find_groups(user):
    groups = [
        Group('global'),
        group_for_user(user)
    ]

    return groups


def subscribe_to_group(group, reply_channel):
    return Group(group).add(reply_channel)


def unsubscribe_from_group(group, reply_channel):
    return Group(group).discard(reply_channel)


@jwt_create_channel_session
def handle_connect(message):
    message.reply_channel.send({'accept': True})
    groups = find_groups(message.user)
    for group in groups:
        group.add(message.reply_channel)


@jwt_retrieve_channel_session
def handle_disconnect(message):
    groups = find_groups(message.user)
    for group in groups:
        group.discard(message.reply_channel)


@jwt_retrieve_channel_session
def handle_message(message):
    '''
    Example - broadcast message to everybody:

    notify_group(Group("global"), {
        "message": message['text']
    })
    '''
    payload = message.content['text'].split(':')
    if payload[0] == 'SUBSCRIBE':
        subscribe_to_group(payload[1], message.reply_channel)
    elif payload[0] == 'UNSUBSCRIBE':
        unsubscribe_from_group(payload[1], message.reply_channel)
