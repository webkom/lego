from django.conf import settings
from django.core.cache import caches
from django.http import HttpResponse, JsonResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

import requests
import sentry_sdk
from authlib.integrations.base_client.errors import MismatchingStateError
from authlib.integrations.django_client import OAuth
from requests import Response
from structlog import get_logger

from lego.apps.users.models import User
from lego.apps.users.serializers.student_confirmation import FeideAuthorizeSerializer

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


def get_feide_groups(bearer: str) -> Response:
    return requests.get(
        f"{settings.FEIDE_GROUPS_ENDPOINT}",
        headers={"Authorization": f"Bearer {bearer}"},
    )


class OIDCViewSet(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)

    @action(detail=False, methods=["GET"])
    def authorize(self, request: Request) -> JsonResponse:
        redirect_uri = f"{settings.FRONTEND_URL}/users/me/settings/student-confirmation"
        auth_uri = oauth.feide.authorize_redirect(request, redirect_uri).url
        return JsonResponse(
            FeideAuthorizeSerializer({"url": auth_uri}).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["GET"])
    def validate(self, request: Request) -> HttpResponse:
        programme_names = []

        try:
            token = oauth.feide.authorize_access_token(request)
            validation_status = "success"
        except MismatchingStateError as e:
            sentry_sdk.capture_message("Failed while validating access token", "fatal")
            sentry_sdk.capture_exception(error=e)
            return JsonResponse(
                {
                    "status": "error",
                    "detail": "Error when validating OAUTH acccess token",
                }
            )

        user: User = request.user  # type: ignore[assignment]

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
