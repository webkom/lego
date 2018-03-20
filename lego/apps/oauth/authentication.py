from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from structlog import get_logger

from lego.apps.stats.utils import track

log = get_logger()


class Authentication(OAuth2Authentication):
    """
    Attach the OAuth2 user to the log context.
    """

    def authenticate(self, request):
        authentication = super().authenticate(request)

        if authentication:
            user = authentication[0]
            log.bind(current_user=user.id)
            track(user, 'authenticate')

        return authentication
