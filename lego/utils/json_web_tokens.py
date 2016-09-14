from lego.apps.users.serializers import MeSerializer


def response_handler(token, user=None, request=None):
    return {
        'token': token,
        'user': MeSerializer(user).data
    }
