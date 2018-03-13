from prometheus_client import Counter
from rest_framework_jwt.settings import api_settings

from lego.apps.stats.utils import track
from lego.apps.users.serializers.users import MeSerializer

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

AUTHENTICATE_JWT_COUNTER = Counter('authenticate_jwt', 'JWT authentication')


def response_handler(token, user=None, request=None):
    AUTHENTICATE_JWT_COUNTER.inc()
    track(user, 'authenticate')
    return {'token': token, 'user': MeSerializer(user).data}


def get_jwt_token(user):
    payload = jwt_payload_handler(user)
    token = jwt_encode_handler(payload)
    return response_handler(token, user)
