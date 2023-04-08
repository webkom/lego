from urllib.parse import parse_qs

from django.db import close_old_connections
from rest_framework import exceptions

from channels.db import database_sync_to_async

from lego.apps.jwt.authentication import Authentication


class JWTQSAuthentication(Authentication):
    @classmethod
    def get_token_from_request(cls, scope):
        if scope.get("type") != "websocket":
            raise exceptions.AuthenticationFailed("Websocket connection i required")

        query_string = (scope.get("query_string", b"")).decode()
        qs = parse_qs(query_string)
        jwt_param = qs.get("jwt", [])
        if len(jwt_param) != 1:
            raise exceptions.AuthenticationFailed("Invalid JWT query param")
        return jwt_param[0]

    @database_sync_to_async
    def authenticate(self, request):
        return super().authenticate(request)


class JWTAuthenticationMiddleware:
    def __init__(self, inner):
        self.inner = inner
        self.authentication = JWTQSAuthentication()

    async def __call__(self, scope, receive, send):
        # If there are old connecions in the database,
        # authentication will fail. So we make sure to clean up.
        close_old_connections()
        user, token = await self.authentication.authenticate(scope)
        scope["user"] = user
        scope["token"] = token
        return await self.inner(scope, receive, send)
