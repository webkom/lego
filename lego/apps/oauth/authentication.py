from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from prometheus_client import Counter
from structlog import get_logger

from lego.apps.stats.utils import track

log = get_logger()
AUTHENTICATE_OAUTH2_COUNTER = Counter('authenticate_oauth2', 'OAuth2 authentication')


class Authentication(OAuth2Authentication):
    """
    Attach the OAuth2 user to the log context.
    """

    def authenticate(self, request):
        authentication = super().authenticate(request)

        if authentication:
            AUTHENTICATE_OAUTH2_COUNTER.inc()
            user = authentication[0]
            log.bind(current_user=user.id)
            track(user, 'authenticate')

        return authentication
