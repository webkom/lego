from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from structlog import get_logger

log = get_logger()


class Authentication(JSONWebTokenAuthentication):
    """
    Attach the JWT user to the log context.
    """

    def authenticate(self, request):
        authentication = super().authenticate(request)

        if authentication:
            user = authentication[0]
            log.bind(current_user=user.id)

        return authentication
