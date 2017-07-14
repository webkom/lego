from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from structlog import get_logger

from lego.apps.stats.statsd_client import statsd

log = get_logger()


class Authentication(OAuth2Authentication):
    """
    Attach the OAuth2 user to the log context.
    """

    def authenticate(self, request):
        authentication = super().authenticate(request)

        if authentication:
            statsd.incr('authentication.authenticate.oauth', 1)
            user = authentication[0]
            log.bind(current_user=user.username)

        return authentication
