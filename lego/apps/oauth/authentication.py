from oauth2_provider.ext.rest_framework import OAuth2Authentication
from structlog import get_logger

log = get_logger()


class Authentication(OAuth2Authentication):
    """
    Attach the OAuth2 user to the log context.
    """

    def authenticate(self, request):
        authentication = super().authenticate(request)

        if authentication:
            user = authentication[0]
            log.bind(current_user=user.username)

        return authentication
