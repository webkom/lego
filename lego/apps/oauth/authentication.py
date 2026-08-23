from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from structlog import get_logger

log = get_logger()

USER_SCOPE_PATHS = frozenset(
    {
        "/api/v1/users/oauth2_userdata/",
        "/api/v1/search-autocomplete/",
    }
)


class Authentication(OAuth2Authentication):
    """
    Attach the OAuth2 user to the log context.
    """

    def authenticate(self, request):
        authentication = super().authenticate(request)

        if not authentication:
            return None
        user, token = authentication

        if user is None:
            # django-oauth-toolkit (<2.0) issues client_credentials tokens
            # without a user. Such machine tokens act as the application's
            # owner, so the owner's permissions are the credential's ceiling.
            application = token.application
            if (
                application.authorization_grant_type
                != application.GRANT_CLIENT_CREDENTIALS
                or application.client_type != application.CLIENT_CONFIDENTIAL
            ):
                return None
            user = application.user
            if user is None or not user.is_active:
                return None
            authentication = (user, token)

        log.bind(current_user=user.id)

        if token.allow_scopes(["all"]):
            return authentication

        # Paths accessible to 'user' scoped tokens. All other endpoints require 'all'
        #
        # Is needed to allow client applications (like admissions) to search users without
        # holding 'all' access
        if token.allow_scopes(["user"]) and request.path in USER_SCOPE_PATHS:
            return authentication
        return None
