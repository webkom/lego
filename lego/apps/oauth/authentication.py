from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from structlog import get_logger

log = get_logger()


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

        # Allow "user" scope for oauth2_userdata endpoint
        if (
            token.allow_scopes(["user"])
            and request.path == "/api/v1/users/oauth2_userdata/"
        ):
            return authentication

        # Allow "aoc" scope for oauth2_userdata and users list endpoints
        if token.allow_scopes(["aoc"]):
            allowed_paths = [
                "/api/v1/users/oauth2_userdata/",
                "/api/v1/users/"
            ]
            if request.path in allowed_paths:
                return authentication

        return None
