from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from structlog import get_logger

from lego.apps.stats.statsd_client import statsd

log = get_logger()


class Authentication(JSONWebTokenAuthentication):
    """
    Attach the JWT user to the log context.
    """

    def authenticate(self, request):
        authentication = super().authenticate(request)

        if authentication:
            statsd.incr('authentication.authenticate.jwt', 1)
            user = authentication[0]
            log.bind(current_user=user.username)

        return authentication
