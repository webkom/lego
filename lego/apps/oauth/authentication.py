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

        application = token.application
        if (
            application is not None
            and application.authorization_grant_type
            == application.GRANT_CLIENT_CREDENTIALS
        ):
            # client_credentials tokens have no user; they act as the owning
            # application's user, whose permissions are the credential's
            # ceiling. The FK bypasses the soft-delete manager, so `deleted`
            # needs its own check.
            owner = application.user
            if (
                application.client_type != application.CLIENT_CONFIDENTIAL
                or owner is None
                or owner.deleted
                or not owner.is_active
                or (user is not None and user.pk != owner.pk)
            ):
                return None
            user = owner
            authentication = (user, token)
            log.bind(current_application=application.id)
        elif user is None:
            # No configured flow produces a user-less non-machine token.
            return None

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
