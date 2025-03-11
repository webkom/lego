from enum import Enum
from unittest import mock

from django.http import HttpResponseRedirect
from rest_framework import status

from lego.apps.users import constants
from lego.apps.users.models import AbakusGroup, User
from lego.utils.test_utils import BaseAPITestCase


class MockFeideOAUTH:
    _auth_url = "https://auth.mock-feide.no/auth"

    def __init__(self, token="valid_token"):
        self.token = token

    def authorize_redirect(self, request, redirect_url):
        return HttpResponseRedirect(self._auth_url)

    def authorize_access_token(self, request):
        return _token(self.token)

    def userinfo(self, **kwargs):
        uid = f"{kwargs.get('token')['access_token']}@ntnu.no"
        return {"https://n.feide.no/claims/eduPersonPrincipalName": uid}


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

        self.client.force_authenticate(self.user_without_student_confirmation)

    def test_with_unauthenticated_user(self, *args):
        self.client.force_authenticate(None)
        response = self.client.get(_get_validate_url())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @mock.patch("lego.apps.users.views.oidc.oauth.feide", MockFeideOAUTH(Token.DATA))
    def test_data_1st(self, *args):
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
        response = self.client.get(_get_validate_url())

        json = response.json()
        self.assertEqual(json.get("status"), "success")
        self.assertEqual(
            self.user_with_student_confirmation.student_username,
            f"{str(Token.DATA).lower()}",
        )

        self.client.force_authenticate(self.user_without_student_confirmation)
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
