from oauth2_provider.ext.rest_framework import OAuth2Authentication
from prometheus_client import Counter
from structlog import get_logger

log = get_logger()


authenticate_oauth = Counter('authenticate_oauth', 'Track oauth authenticate')


class Authentication(OAuth2Authentication):
    """
    Attach the OAuth2 user to the log context.
    """

    def authenticate(self, request):
        authentication = super().authenticate(request)

        if authentication:
            authenticate_oauth.inc()
            user = authentication[0]
            log.bind(current_user=user.username)

        return authentication
