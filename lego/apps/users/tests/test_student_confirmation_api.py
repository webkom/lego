import json
import time
from enum import Enum
from unittest import mock
from urllib.parse import parse_qs, urlparse

from django.conf import settings
from rest_framework import status
from rest_framework.test import APIClient

import requests
from authlib.integrations.base_client.errors import OAuthError
from authlib.jose import JsonWebKey, jwt as jose_jwt

from lego.apps.users import constants
from lego.apps.users.models import AbakusGroup, User
from lego.apps.users.views.oidc import oauth, oauth_cache
from lego.utils.test_utils import BaseAPITestCase


class MockFeideOAUTH:
    _auth_url = "https://auth.mock-feide.no/auth"

    def __init__(self, token="valid_token", state="state"):
        self.token = token
        self._state = state

    def create_authorization_url(self, redirect_uri):
        return {"url": self._auth_url, "state": self._state, "nonce": "nonce"}

    def fetch_access_token(self, **kwargs):
        return _token(self.token)

    def parse_id_token(self, token, nonce):
        return None

    def userinfo(self, **kwargs):
        uid = f"{kwargs.get('token')['access_token']}@ntnu.no"
        return {"https://n.feide.no/claims/eduPersonPrincipalName": uid}


class MockFeideOAUTHInvalidGrant(MockFeideOAUTH):
    def fetch_access_token(self, **kwargs):
        raise OAuthError(error="invalid_grant")


mockFeide = MockFeideOAUTH()


class Token(Enum):
    DATA = "data"
    KOMTEK = "komtek"
    DATA_MASTER = "data_midt"
    KOMTEK_MASTER = "komtek_master"
    SECCLO_MASTER = "secclo_master"
    MULTI_OTHER = "others"
    INDOK = "indok"


def _token(token):
    return {"access_token": token}


data_resp = [
    {
        "id": "fc:fs:fs:prg:ntnu.no:MTDT",
        "type": "fc:fs:prg",
        "displayName": "Computer Science",
        "membership": {
            "basic": "member",
            "active": True,
            "displayName": "Student",
            "fsroles": ["STUDENT"],
        },
        "parent": "fc:org:ntnu.no",
        "url": "http://www.ntnu.no/studier/mtdt",
    }
]

komtek_resp = [
    {
        "id": "fc:fs:fs:prg:ntnu.no:MTKOM",
        "type": "fc:fs:prg",
        "displayName": "Communication Technology",
        "membership": {
            "basic": "member",
            "active": True,
            "displayName": "Student",
            "fsroles": ["STUDENT"],
        },
        "parent": "fc:org:ntnu.no",
        "url": "http://www.ntnu.no/studier/mtkom",
    }
]

data_master_resp = [
    {
        "id": "fc:fs:fs:prg:ntnu.no:MIDT",
        "type": "fc:fs:prg",
        "displayName": "Computer Science",
    }
]

komtek_master_resp = [
    {
        "id": "fc:fs:fs:prg:ntnu.no:MSTCNNS",
        "type": "fc:fs:prg",
        "displayName": "Digital Infrastructure and Cyber Security",
    }
]

secclo_master_resp = [
    {
        "id": "fc:fs:fs:prg:ntnu.no:MSSECCLO",
        "type": "fc:fs:prg",
        "displayName": "Security and Cloud Computing",
    }
]

multi_other_resp = [
    {
        "id": "fc:fs:fs:prg:ntnu.no:MSIT",
        "type": "fc:fs:prg",
        "displayName": "Informatikk",
    },
    {
        "id": "fc:fs:fs:prg:ntnu.no:BIT",
        "type": "fc:fs:prg",
        "displayName": "Informatikk (Bachelor)",
    },
]

indok_resp = [
    {
        "id": "fc:fs:fs:prg:ntnu.no:MTIOT",
        "type": "fc:fs:prg",
        "displayName": "Industriell økonomi og teknologiledelse",
    }
]


def mocked_feide_get(token):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

        def raise_for_status(self):
            return None

    if token == Token.DATA:
        return MockResponse(data_resp, 200)
    elif token == Token.KOMTEK:
        return MockResponse(komtek_resp, 200)
    elif token == Token.DATA_MASTER:
        return MockResponse(data_master_resp, 200)
    elif token == Token.KOMTEK_MASTER:
        return MockResponse(komtek_master_resp, 200)
    elif token == Token.SECCLO_MASTER:
        return MockResponse(secclo_master_resp, 200)
    elif token == Token.MULTI_OTHER:
        return MockResponse(multi_other_resp, 200)
    elif token == Token.INDOK:
        return MockResponse(indok_resp, 200)


def _get_oidc_url():
    return "/api/v1/oidc/"


def _get_oidc_authorize_url():
    return f"{_get_oidc_url()}authorize/"


def _get_oidc_validate_url(code, state):
    return f"{_get_oidc_url()}validate/?code={code}&state={state}"


def _get_validate_url():
    return _get_oidc_validate_url("code", "state")


@mock.patch("lego.apps.users.views.oidc.oauth.feide", mockFeide)
class AuthorizeOIDCAPITestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_users.yaml"]

    def setUp(self):
        self.user_with_student_confirmation = User.objects.get(username="test1")
        self.user_without_student_confirmation = User.objects.get(username="test2")

    def test_with_unauthenticated_user(self, *args):
        response = self.client.get(_get_oidc_authorize_url())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_with_authenticated_user(self, *args):
        AbakusGroup.objects.get(name="Users").add_user(
            self.user_without_student_confirmation
        )
        self.client.force_authenticate(self.user_without_student_confirmation)
        response = self.client.get(_get_oidc_authorize_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("url"), mockFeide._auth_url)


@mock.patch("lego.apps.users.views.oidc.get_feide_groups", side_effect=mocked_feide_get)
class ValidateOIDCAPITestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_users.yaml"]

    _test_student_confirmation_data = {
        "student_username": "newteststudentusername",
        "course": constants.DATA,
        "member": True,
        "captcha_response": "testCaptcha",
    }

    def setUp(self):
        self.abakus_group = AbakusGroup.objects.get(name="Abakus")
        self.grade_data_1 = AbakusGroup.objects.create(
            name=constants.FIRST_GRADE_DATA, type=constants.GROUP_GRADE
        )
        self.grade_data_4 = AbakusGroup.objects.create(
            name=constants.FOURTH_GRADE_DATA, type=constants.GROUP_GRADE
        )
        self.grade_komtek_1 = AbakusGroup.objects.create(
            name=constants.FIRST_GRADE_KOMTEK, type=constants.GROUP_GRADE
        )
        self.grade_komtek_4 = AbakusGroup.objects.create(
            name=constants.FOURTH_GRADE_KOMTEK, type=constants.GROUP_GRADE
        )

        self.user_with_student_confirmation = User.objects.get(username="test1")
        self.grade_data_4.add_user(self.user_with_student_confirmation)
        self.abakus_group.add_user(self.user_with_student_confirmation)
        self.user_without_student_confirmation = User.objects.get(username="test2")

        oauth_cache.clear()

        self.client.force_authenticate(self.user_without_student_confirmation)

    def _authorize(self):
        self.client.get(_get_oidc_authorize_url())

    def test_with_unauthenticated_user(self, *args):
        self.client.force_authenticate(None)
        response = self.client.get(_get_validate_url())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @mock.patch("lego.apps.users.views.oidc.oauth.feide", MockFeideOAUTH(Token.DATA))
    def test_data_1st(self, *args):
        self._authorize()
        response = self.client.get(_get_validate_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json = response.json()
        self.assertEqual(json.get("status"), "success")
        self.assertEqual(json.get("studyProgrammes")[0], data_resp[0]["displayName"])
        self.assertEqual(
            self.user_without_student_confirmation.grade.id, self.grade_data_1.id
        )
        self.assertTrue(
            self.user_without_student_confirmation.abakus_groups.filter(
                pk=self.abakus_group.pk
            ).exists()
        )

    @mock.patch("lego.apps.users.views.oidc.oauth.feide", MockFeideOAUTH(Token.KOMTEK))
    def test_komtek_1st(self, *args):
        self._authorize()
        response = self.client.get(_get_validate_url())

        json = response.json()
        self.assertEqual(json.get("status"), "success")
        self.assertEqual(json.get("studyProgrammes")[0], komtek_resp[0]["displayName"])
        self.assertEqual(
            self.user_without_student_confirmation.grade.id, self.grade_komtek_1.id
        )
        self.assertTrue(
            self.user_without_student_confirmation.abakus_groups.filter(
                pk=self.abakus_group.pk
            ).exists()
        )

    @mock.patch(
        "lego.apps.users.views.oidc.oauth.feide", MockFeideOAUTH(Token.DATA_MASTER)
    )
    def test_data_4th(self, *args):
        self._authorize()
        response = self.client.get(_get_validate_url())

        json = response.json()
        self.assertEqual(json.get("status"), "success")
        self.assertEqual(
            json.get("studyProgrammes")[0], data_master_resp[0]["displayName"]
        )
        self.assertEqual(
            self.user_without_student_confirmation.grade.id, self.grade_data_4.id
        )
        self.assertTrue(
            self.user_without_student_confirmation.abakus_groups.filter(
                pk=self.abakus_group.pk
            ).exists()
        )

    @mock.patch(
        "lego.apps.users.views.oidc.oauth.feide", MockFeideOAUTH(Token.KOMTEK_MASTER)
    )
    def test_komtek_4th(self, *args):
        self._authorize()
        response = self.client.get(_get_validate_url())

        json = response.json()
        self.assertEqual(json.get("status"), "success")
        self.assertEqual(
            json.get("studyProgrammes")[0], komtek_master_resp[0]["displayName"]
        )
        self.assertEqual(
            self.user_without_student_confirmation.grade.id, self.grade_komtek_4.id
        )
        self.assertTrue(
            self.user_without_student_confirmation.abakus_groups.filter(
                pk=self.abakus_group.pk
            ).exists()
        )

    @mock.patch(
        "lego.apps.users.views.oidc.oauth.feide", MockFeideOAUTH(Token.SECCLO_MASTER)
    )
    def test_secclo_master(self, *args):
        self._authorize()
        response = self.client.get(_get_validate_url())

        json = response.json()
        self.assertEqual(json.get("status"), "success")
        self.assertEqual(
            json.get("studyProgrammes")[0], secclo_master_resp[0]["displayName"]
        )
        self.assertEqual(
            self.user_without_student_confirmation.grade.id, self.grade_komtek_4.id
        )
        self.assertTrue(
            self.user_without_student_confirmation.abakus_groups.filter(
                pk=self.abakus_group.pk
            ).exists()
        )

    @mock.patch(
        "lego.apps.users.views.oidc.oauth.feide", MockFeideOAUTH(Token.MULTI_OTHER)
    )
    def test_with_other_study_informatics(self, *args):
        self._authorize()
        response = self.client.get(_get_validate_url())

        json = response.json()
        self.assertEqual(json.get("status"), "unauthorized")
        self.assertEqual(
            json.get("studyProgrammes")[0], multi_other_resp[0]["displayName"]
        )
        self.assertEqual(len(json.get("studyProgrammes")), len(multi_other_resp))
        self.assertIsNone(self.user_without_student_confirmation.grade)
        self.assertFalse(
            self.user_without_student_confirmation.abakus_groups.filter(
                pk=self.abakus_group.pk
            ).exists()
        )

    @mock.patch("lego.apps.users.views.oidc.oauth.feide", MockFeideOAUTH(Token.DATA))
    def test_valid_study_existing_grade(self, *args):
        """
        You should keep your grade when re-authenticating
        """
        self.client.force_authenticate(self.user_with_student_confirmation)
        self._authorize()
        response = self.client.get(_get_validate_url())

        json = response.json()
        self.assertEqual(json.get("studyProgrammes")[0], data_resp[0]["displayName"])

        self.assertNotEqual(
            self.user_with_student_confirmation.grade.id, self.grade_data_1.id
        )
        self.assertEqual(
            self.user_with_student_confirmation.grade.id, self.grade_data_4.id
        )
        self.assertTrue(
            self.user_with_student_confirmation.abakus_groups.filter(
                pk=self.abakus_group.pk
            ).exists()
        )

    @mock.patch("lego.apps.users.views.oidc.oauth.feide", MockFeideOAUTH(Token.INDOK))
    def test_switch_to_indok(self, *args):
        """
        You should keep your validation status and grade when switching to indok
        """
        self.client.force_authenticate(self.user_with_student_confirmation)
        self._authorize()
        response = self.client.get(_get_validate_url())

        json = response.json()
        self.assertEqual(json.get("studyProgrammes")[0], indok_resp[0]["displayName"])
        self.assertEqual(json.get("status"), "success")
        self.assertEqual(json.get("grade"), self.grade_data_4.name)

        self.assertEqual(
            self.user_with_student_confirmation.grade.id, self.grade_data_4.id
        )
        self.assertTrue(self.user_with_student_confirmation.is_verified_student())
        self.assertTrue(
            self.user_with_student_confirmation.abakus_groups.filter(
                pk=self.abakus_group.pk
            ).exists()
        )

    @mock.patch("lego.apps.users.views.oidc.oauth.feide", MockFeideOAUTH(Token.DATA))
    def test_multiple_users_one_feide(self, *args):
        """
        It should only be allowed to auth a single user with a feide account
        """
        self.client.force_authenticate(self.user_with_student_confirmation)
        self._authorize()
        response = self.client.get(_get_validate_url())

        json = response.json()
        self.assertEqual(json.get("status"), "success")
        self.assertEqual(
            self.user_with_student_confirmation.student_username,
            f"{str(Token.DATA).lower()}",
        )

        self.client.force_authenticate(self.user_without_student_confirmation)
        self._authorize()
        response = self.client.get(_get_validate_url())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        json = response.json()
        self.assertEqual(json.get("status"), "error")
        user_without_student_confirmation = User.objects.get(username="test2")
        self.assertNotEqual(
            self.user_with_student_confirmation.student_username,
            user_without_student_confirmation.student_username,
        )
        self.assertFalse(
            self.user_without_student_confirmation.abakus_groups.filter(
                pk=self.abakus_group.pk
            ).exists()
        )

    @mock.patch("lego.apps.users.views.oidc.oauth.feide", MockFeideOAUTH(Token.DATA))
    def test_without_prior_authorize(self, *args):
        response = self.client.get(_get_validate_url())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get("status"), "error")

    @mock.patch("lego.apps.users.views.oidc.oauth.feide", MockFeideOAUTH(Token.DATA))
    def test_with_mismatching_state(self, *args):
        """
        A stale or wrong callback must not consume the pending flow's state
        """
        self._authorize()
        response = self.client.get(_get_oidc_validate_url("code", "wrong-state"))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get("status"), "error")

        response = self.client.get(_get_validate_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("status"), "success")

    def test_completing_first_of_two_started_flows(self, *args):
        """
        Starting a second flow (e.g. another tab) must not invalidate the
        first one
        """
        with mock.patch(
            "lego.apps.users.views.oidc.oauth.feide",
            MockFeideOAUTH(Token.DATA, state="state-a"),
        ):
            self._authorize()
        with mock.patch(
            "lego.apps.users.views.oidc.oauth.feide",
            MockFeideOAUTH(Token.DATA, state="state-b"),
        ):
            self._authorize()
        with mock.patch(
            "lego.apps.users.views.oidc.oauth.feide", MockFeideOAUTH(Token.DATA)
        ):
            response = self.client.get(_get_oidc_validate_url("code", "state-a"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("status"), "success")

    @mock.patch("lego.apps.users.views.oidc.oauth.feide", MockFeideOAUTH(Token.DATA))
    def test_with_replayed_state(self, *args):
        self._authorize()
        first = self.client.get(_get_validate_url())
        self.assertEqual(first.status_code, status.HTTP_200_OK)
        second = self.client.get(_get_validate_url())
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)

    @mock.patch("lego.apps.users.views.oidc.oauth.feide", MockFeideOAUTH(Token.DATA))
    def test_with_state_from_another_user(self, *args):
        """
        The state is bound to the user who started the flow, so no session
        cookie is required and another user cannot complete the flow
        """
        self._authorize()
        self.client.force_authenticate(self.user_with_student_confirmation)
        response = self.client.get(_get_validate_url())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @mock.patch("lego.apps.users.views.oidc.oauth.feide", MockFeideOAUTHInvalidGrant())
    def test_with_rejected_authorization_code(self, *args):
        self._authorize()
        response = self.client.get(_get_validate_url())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get("status"), "error")


FEIDE_METADATA = {
    "issuer": "https://feide.test",
    "authorization_endpoint": "https://feide.test/oauth/authorization",
    "token_endpoint": "https://feide.test/oauth/token",
    "userinfo_endpoint": "https://feide.test/openid/userinfo",
    "jwks_uri": "https://feide.test/openid/jwks",
    "id_token_signing_alg_values_supported": ["RS256"],
}


def _json_response(url, data):
    response = requests.Response()
    response.status_code = 200
    response.url = url
    response.headers["Content-Type"] = "application/json"
    response._content = json.dumps(data).encode()
    return response


class FeideOIDCFlowTestCase(BaseAPITestCase):
    """
    Runs authorize and validate through the real authlib client against a
    stubbed Feide, using a separate cookie-less client for each request.
    The webapp calls the API cross-origin and never sends cookies, so this
    guards against the flow depending on session state again (which broke
    with the authlib >= 1.6 session-bound state)
    """

    fixtures = ["test_abakus_groups.yaml", "test_users.yaml"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.jwk = JsonWebKey.generate_key("RSA", 2048, is_private=True)

    def setUp(self):
        self.abakus_group = AbakusGroup.objects.get(name="Abakus")
        self.grade_data_1 = AbakusGroup.objects.create(
            name=constants.FIRST_GRADE_DATA, type=constants.GROUP_GRADE
        )
        self.user = User.objects.get(username="test2")
        self.expected_nonce = None
        for attribute, value in (
            ("client_id", "test-client-id"),
            ("client_secret", "test-client-secret"),
            ("server_metadata", {}),
        ):
            patcher = mock.patch.object(oauth.feide, attribute, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def _make_id_token(self):
        now = int(time.time())
        claims = {
            "iss": FEIDE_METADATA["issuer"],
            "sub": "feide-subject",
            "aud": "test-client-id",
            "iat": now,
            "exp": now + 300,
            "nonce": self.expected_nonce,
        }
        return jose_jwt.encode({"alg": "RS256"}, claims, self.jwk).decode()

    def _fake_feide_send(self, session, request, **kwargs):
        if request.url == settings.FEIDE_OIDC_CONFIGURATION_ENDPOINT:
            return _json_response(request.url, FEIDE_METADATA)
        if request.url == FEIDE_METADATA["jwks_uri"]:
            return _json_response(request.url, {"keys": [self.jwk.as_dict()]})
        if request.url == FEIDE_METADATA["token_endpoint"]:
            body = parse_qs(request.body)
            self.assertEqual(body["code"], ["test-code"])
            self.assertEqual(body["grant_type"], ["authorization_code"])
            self.assertEqual(
                body["redirect_uri"],
                [f"{settings.FRONTEND_URL}/users/me/settings/student-confirmation"],
            )
            self.assertTrue(
                request.headers.get("Authorization", "").startswith("Basic ")
            )
            return _json_response(
                request.url,
                {
                    "access_token": "feide-access-token",
                    "token_type": "Bearer",
                    "expires_in": 3600,
                    "id_token": self._make_id_token(),
                },
            )
        if request.url == FEIDE_METADATA["userinfo_endpoint"]:
            self.assertEqual(
                request.headers.get("Authorization"), "Bearer feide-access-token"
            )
            return _json_response(
                request.url,
                {
                    "https://n.feide.no/claims/eduPersonPrincipalName": "teststudent@ntnu.no"
                },
            )
        if request.url == settings.FEIDE_GROUPS_ENDPOINT:
            return _json_response(request.url, data_resp)
        raise AssertionError(f"Unexpected request to {request.url}")

    def _authorize_and_get_callback_params(self, client):
        authorize_response = client.get(_get_oidc_authorize_url())
        self.assertEqual(authorize_response.status_code, status.HTTP_200_OK)
        auth_url = authorize_response.json()["url"]
        self.assertTrue(auth_url.startswith(FEIDE_METADATA["authorization_endpoint"]))
        query = parse_qs(urlparse(auth_url).query)
        self.expected_nonce = query["nonce"][0]
        return query["state"][0]

    def test_flow_succeeds_without_session_cookies(self):
        with mock.patch.object(
            requests.sessions.Session,
            "send",
            autospec=True,
            side_effect=self._fake_feide_send,
        ):
            authorize_client = APIClient()
            authorize_client.force_authenticate(self.user)
            state = self._authorize_and_get_callback_params(authorize_client)

            validate_client = APIClient()
            validate_client.force_authenticate(self.user)
            self.assertEqual(len(validate_client.cookies), 0)
            validate_response = validate_client.get(
                _get_oidc_validate_url("test-code", state)
            )

        self.assertEqual(validate_response.status_code, status.HTTP_200_OK)
        json_body = validate_response.json()
        self.assertEqual(json_body["status"], "success")
        self.assertEqual(json_body["studyProgrammes"], ["Computer Science"])
        self.user.refresh_from_db()
        self.assertEqual(self.user.student_username, "teststudent")

    def test_id_token_with_wrong_nonce_is_rejected(self):
        with mock.patch.object(
            requests.sessions.Session,
            "send",
            autospec=True,
            side_effect=self._fake_feide_send,
        ):
            client = APIClient()
            client.force_authenticate(self.user)
            state = self._authorize_and_get_callback_params(client)
            self.expected_nonce = "attacker-controlled-nonce"
            validate_response = client.get(_get_oidc_validate_url("test-code", state))

        self.assertEqual(validate_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(validate_response.json()["status"], "error")
        self.user.refresh_from_db()
        self.assertIsNone(self.user.student_username)
