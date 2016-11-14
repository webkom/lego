import functools

from channels.handler import AsgiRequest
from channels.sessions import channel_session
from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import AuthenticationFailed

from lego.apps.users.models import User
from lego.authentication import JSONWebTokenAuthenticationQS


def jwt_create_channel_session(func):
    """
    Retrieves the jwt-token from a querystring, and uses this
    to add a .user property to the message. Also adds the
    user pk to the channel session, so the user
    can be retrieved later.
    """
    @channel_session
    @functools.wraps(func)
    def inner(message, *args, **kwargs):
        # WebSocket messages won't contain a method,
        # mock it like channels does in their http_session decorator:
        if 'method' not in message.content:
            message.content['method'] = 'FAKE'
        request = AsgiRequest(message)
        jwt_auth = JSONWebTokenAuthenticationQS()
        try:
            data = jwt_auth.authenticate(request)
            user = data[0] if data else None
        except AuthenticationFailed:
            user = None

        if user:
            message.channel_session['user'] = user.pk

        message.user = user or AnonymousUser()
        return func(message, *args, **kwargs)

    return inner


def jwt_retrieve_channel_session(func):
    """
    Uses the channel session to retrieve and set the authenticated
    user to .user.

    Must be used in combination with jwt_create_channel_session
    """
    @channel_session
    @functools.wraps(func)
    def inner(message, *args, **kwargs):
        pk = message.channel_session.get('user')
        if not pk:
            message.user = AnonymousUser()
        else:
            message.user = User.objects.get(pk=pk)

        return func(message, *args, **kwargs)

    return inner
