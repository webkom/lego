from prometheus_client import Counter
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from structlog import get_logger

log = get_logger()

authenticate_jwt = Counter('authenticate_jwt', 'Track jwt authentication')


class Authentication(JSONWebTokenAuthentication):
    """
    Attach the JWT user to the log context.
    """

    def authenticate(self, request):
        authentication = super().authenticate(request)

        if authentication:
            authenticate_jwt.inc()
            user = authentication[0]
            log.bind(current_user=user.username)

        return authentication
