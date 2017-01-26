from lego.apps.users.serializers.users import MeSerializer


def response_handler(token, user=None, request=None):
    return {
        'token': token,
        'user': MeSerializer(user).data
    }
