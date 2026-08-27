import re

from django.conf import settings
from django.core.cache import caches
from django.db import IntegrityError, transaction
from django.http import HttpResponse, JsonResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

import requests
import sentry_sdk
from authlib.integrations.base_client.errors import OAuthError
from authlib.integrations.django_client import OAuth
from authlib.jose.errors import JoseError
from requests import Response
from structlog import get_logger

from lego.apps.users.models import User
from lego.apps.users.serializers.student_confirmation import FeideAuthorizeSerializer
from lego.apps.users.validators import STUDENT_USERNAME_REGEX

log = get_logger()

oauth_cache = caches["oauth"]

oauth = OAuth(cache=oauth_cache)
oauth.register(
    name="feide",
    client_id=settings.FEIDE_OIDC_CLIENT_ID,
    client_secret=settings.FEIDE_OIDC_CLIENT_SECRET,
    server_metadata_url=settings.FEIDE_OIDC_CONFIGURATION_ENDPOINT,
    client_kwargs={"scope": "openid"},
)

FEIDE_STATE_TTL_SECONDS = 3600


def get_state_cache_key(user_id: int, state: str) -> str:
    return f"feide_oidc_state_{user_id}_{state}"


def get_feide_groups(bearer: str) -> Response:
    return requests.get(
        f"{settings.FEIDE_GROUPS_ENDPOINT}",
        headers={"Authorization": f"Bearer {bearer}"},
    )


def get_uid_from_principalName(principal_name: str) -> str | None:
    regex = rf"(?P<uid>{STUDENT_USERNAME_REGEX})@ntnu.no"

    match = re.match(regex, principal_name)
    if match is not None:
        return match.group("uid")

    return None


class OIDCViewSet(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)

    @action(detail=False, methods=["GET"])
    def authorize(self, request: Request) -> JsonResponse:
        user: User = request.user  # type: ignore[assignment]
        redirect_uri = f"{settings.FRONTEND_URL}/users/me/settings/student-confirmation"
        authorization_data: dict[str, str] = oauth.feide.create_authorization_url(
            redirect_uri
        )
        state_data: dict[str, str] = {
            "nonce": authorization_data["nonce"],
            "redirect_uri": redirect_uri,
        }
        oauth_cache.set(
            get_state_cache_key(user.id, authorization_data["state"]),
            state_data,
            FEIDE_STATE_TTL_SECONDS,
        )
        return JsonResponse(
            FeideAuthorizeSerializer({"url": authorization_data["url"]}).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["GET"])
    def validate(self, request: Request) -> HttpResponse:
        programme_names = []

        user: User = request.user  # type: ignore[assignment]

        code = request.query_params.get("code")
        state = request.query_params.get("state")

        state_data: dict[str, str] | None = None
        if code and state:
            cache_key = get_state_cache_key(user.id, state)
            state_data = oauth_cache.get(cache_key)
            if state_data is not None and not oauth_cache.delete(cache_key):
                state_data = None

        if state_data is None:
            sentry_sdk.capture_message(
                "Feide validation attempted with unknown or already used state",
                "warning",
            )
            return JsonResponse(
                {
                    "status": "error",
                    "detail": "Error when validating OAuth access token",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = oauth.feide.fetch_access_token(
                redirect_uri=state_data["redirect_uri"], code=code
            )
            oauth.feide.parse_id_token(token, nonce=state_data["nonce"])
        except (OAuthError, JoseError) as e:
            sentry_sdk.capture_message("Failed while validating access token", "fatal")
            sentry_sdk.capture_exception(error=e)
            return JsonResponse(
                {
                    "status": "error",
                    "detail": "Error when validating OAuth access token",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        userinfo = oauth.feide.userinfo(token=token)
        principal_name = userinfo["https://n.feide.no/claims/eduPersonPrincipalName"]
        uid = get_uid_from_principalName(principal_name)
        if uid is None:
            sentry_sdk.capture_message(
                "Could not extract student username from principal_name",
                "fatal",
                extras={"principal_name": principal_name},
            )
            validation_status = "error"
        else:
            try:
                validation_status = "success"
                with transaction.atomic():
                    user.student_username = uid
                    user.save()

            except IntegrityError:
                return JsonResponse(
                    {
                        "status": "error",
                        "detail": f"The feide account {uid} is already linked to another user",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            groups_res = get_feide_groups(token["access_token"])
            groups_res.raise_for_status()

            groups = groups_res.json()
            student_validation = user.verify_student(feide_groups=groups)
            if not student_validation:
                validation_status = "unauthorized"

            programme_names = [
                p["displayName"]
                for p in filter(lambda g: g["type"] == "fc:fs:prg", groups)
            ]

        except requests.HTTPError as e:
            sentry_sdk.capture_message("Failed while obtaining FEIDE groups", "fatal")
            sentry_sdk.capture_exception(error=e)
            validation_status = "error"

        return JsonResponse(
            {
                "status": validation_status,
                "studyProgrammes": programme_names,
                "grade": user.grade.name if user.grade is not None else None,
            },
            status=status.HTTP_200_OK,
        )
