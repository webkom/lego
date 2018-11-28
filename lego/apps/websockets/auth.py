from urllib.parse import parse_qs

from rest_framework import exceptions

from lego.apps.jwt.authentication import Authentication


class JWTQSAuthentication(Authentication):
    def get_jwt_value(self, scope):
        if scope.get("type") != "websocket":
            raise exceptions.AuthenticationFailed("Websocket connection i required")

        query_string = (scope.get("query_string", b"")).decode()
        qs = parse_qs(query_string)
        jwt_param = qs.get("jwt", [])
        if len(jwt_param) != 1:
            raise exceptions.AuthenticationFailed("Invalid JWT query param")
        return jwt_param[0]


class JWTAuthenticationMiddleware:
    def __init__(self, inner):
        self.inner = inner
        self.authentication = JWTQSAuthentication()

    def __call__(self, scope):
        user, token = self.authentication.authenticate(scope)
        scope["user"] = user
        scope["token"] = token
        return self.inner(scope)
