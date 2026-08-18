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
        log.bind(current_user=user.id)

        if token.allow_scopes(["all"]):
            return authentication

        # Paths a `user`-scoped token may reach. Everything else requires `all`.
        #
        # search-autocomplete is read-only and already AllowAny for session
        # users, and every hit is filtered through `has_permission` before it is
        # returned, so a token here sees no more than the person holding it
        # would see in the web UI. It is allowlisted so applications like
        # admissions can let a signed-in member look someone up by name without
        # holding an `all`-scoped credential of their own.
        if token.allow_scopes(["user"]) and request.path in USER_SCOPE_PATHS:
            return authentication
        return None
