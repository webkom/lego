from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from lego.apps.surveys.models import Survey
from lego.apps.users.models import AbakusGroup, User


def _get_list_url():
    return reverse("api:v1:survey-list")


def _get_detail_url(pk):
    return reverse("api:v1:survey-detail", kwargs={"pk": pk})


def _get_token_url(pk):
    return reverse("api:v1:survey-results-detail", kwargs={"pk": pk})


_test_surveys = [
    # 0: To test editing regular survey fields. Usually to edit the fixture surveys.
    {
        "title": "Test",
        "event": 3,
        "activeFrom": "2018-02-13T19:15:51.162564Z",
        "questions": [],
    },
    # 1: To test editing question fields. Usually to edit the fixture questions.
    {
        "questions": [
            {
                "id": 1,
                "questionType": "multiple_choice",
                "questionText": "Hva var good?",
                "mandatory": False,
                "relativeIndex": 1,
                "options": [],
                "display_type": "pie_chart",
            },
            {
                "id": 2,
                "questionType": "text_field",
                "questionText": "Noe feedback?",
                "mandatory": False,
                "relativeIndex": 2,
                "options": [],
            },
            {
                "id": 3,
                "questionType": "single_choice",
                "questionText": "Hva var best?",
                "mandatory": True,
                "relativeIndex": 3,
                "options": [],
                "display_type": "bar_chart",
            },
        ]
    },
    # 2: To test adding and removing questions, usually to be applied after [1].
    {
        "questions": [
            {
                "id": 1,
                "questionType": "multiple_choice",
                "questionText": "Hva var good?",
                "mandatory": False,
                "relativeIndex": 1,
                "options": [],
            },
            {
                "id": 3,
                "questionType": "single_choice",
                "questionText": "Hva var best?",
                "mandatory": True,
                "relativeIndex": 2,
                "options": [],
            },
            {
                "questionType": "multiple_choice",
                "questionText": "Hva likte du?",
                "mandatory": False,
                "options": [],
                "relativeIndex": 3,
            },
        ]
    },
    # 3: To test editing options. Usually to be applied to the fixtures.
    {
        "questions": [
            {
                "id": 1,
                "options": [
                    {"id": 1, "optionText": "Tja"},
                    {"id": 2, "optionText": "Njei"},
                ],
            }
        ]
    },
    # 4: To test adding and removing options. Usually to be applied after [3].
    {
        "questions": [
            {
                "id": 1,
                "options": [
                    {"id": 2, "optionText": "I guess"},
                    {"optionText": "Ikke egentlig"},
                ],
            }
        ]
    },
]


class SurveyViewSetTestCase(APITestCase):
    fixtures = [
        "test_users.yaml",
        "test_abakus_groups.yaml",
        "test_surveys.yaml",
        "test_events.yaml",
        "test_companies.yaml",
    ]

    def setUp(self):
        self.admin_user = User.objects.get(username="useradmin_test")
        self.admin_group = AbakusGroup.objects.get(name="Bedkom")
        self.admin_group.add_user(self.admin_user)
        self.regular_user = User.objects.get(username="abakule")
        self.regular_group = AbakusGroup.objects.get(name="Abakus")
        self.regular_group.add_user(self.regular_user)
        self.attended_user = User.objects.get(username="test1")
        self.attending_group = AbakusGroup.objects.get(name="Abakom")
        self.attending_group.add_user(self.attended_user)
        self.survey_data = {"title": "Survey", "event": 5, "questions": []}

    # Create
    def test_create_admin(self):
        """Admin users should be able to create surveys"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(_get_list_url(), self.survey_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_regular(self):
        """Regular users should not be able to create surveys"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post(_get_list_url(), self.survey_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_attended(self):
        """Users who attended the event should still not be able to create a survey"""
        self.client.force_authenticate(user=self.attended_user)
        response = self.client.post(_get_list_url(), self.survey_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_anonymous(self):
        """Anonymous users should not be able to create surveys"""
        self.client.force_authenticate(user=None)
        response = self.client.post(_get_list_url(), self.survey_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Fetch detail
    def test_detail_admin(self):
        """Admin users should be able to see detailed surveys"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(_get_detail_url(1))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json())

    def test_detail_regular(self):
        """Users should not be able see detailed surveys"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(_get_detail_url(1))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_detail_attended(self):
        """Users who attended the event should be able to see the survey"""
        self.client.force_authenticate(user=self.attended_user)
        response = self.client.get(_get_detail_url(1))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json())

    def test_detail_anonymous(self):
        """Anonymous users should not be able to see the survey"""
        self.client.force_authenticate(user=None)
        response = self.client.get(_get_detail_url(1))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Detail data
    def test_detail_admin_data(self):
        """Admin users should should get tokens when fetching detail"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(_get_detail_url(1))
        self.assertTrue("token" in response.json())

    def test_detail_attended_data(self):
        """Users who attended the event should not get tokens when fetching detail"""
        self.client.force_authenticate(user=self.attended_user)
        response = self.client.get(_get_detail_url(1))
        self.assertFalse("token" in response.json())

    def test_detail_regular_data(self):
        """Regular users should not get tokens when fetching detail"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(_get_detail_url(1))
        self.assertFalse("token" in response.json())

    def test_detail_anonymous_data(self):
        """Anonymous users should not get tokens when fetching detail"""
        self.client.force_authenticate(user=None)
        response = self.client.get(_get_detail_url(1))
        self.assertFalse("token" in response.json())

    # Fetch list
    def test_list_admin(self):
        """Users with permissions should be able to see surveys list view"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(_get_list_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.json()["results"]
        self.assertEqual(len(results), 2)  # All test surveys

    def test_list_regular(self):
        """Regular users should have permission to see surveys list view"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(_get_list_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.json()["results"]
        self.assertEqual(len(results), 0)  # Has no surveys

    def test_list_attended(self):
        """Users who attended an event should be able to see surveys list view"""
        self.client.force_authenticate(user=self.attended_user)
        response = self.client.get(_get_list_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.json()["results"]
        self.assertEqual(len(results), 1)  # Only one survey

    def test_list_anonymous(self):
        """Anonymous users should not be able to see surveys list view"""
        self.client.force_authenticate(user=None)
        response = self.client.get(_get_list_url())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Fetch filtered list
    def test_filter_list_admin(self):
        """Admin users should be able to see all surveys"""
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get(_get_list_url(), {"user": self.admin_user.id})
        results = response.json()["results"]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results), 0)  # Has no surveys

        response = self.client.get(_get_list_url(), {"user": self.attended_user.id})
        results = response.json()["results"]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results), 1)  # Can view other users surveys

    def test_filter_list_regular(self):
        """Regular users should be able to check if they have surveys"""
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get(_get_list_url(), {"user": self.regular_user.id})
        results = response.json()["results"]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results), 0)  # Has no surveys

        response = self.client.get(_get_list_url(), {"user": self.attended_user.id})
        results = response.json()["results"]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results), 0)  # Can not view other users surveys

    def test_filter_list_attended(self):
        """Attended users should be able to see their own surveys"""
        self.client.force_authenticate(user=self.attended_user)
        response = self.client.get(_get_list_url(), {"user": self.attended_user.id})
        results = response.json()["results"]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results), 1)  # Has one survey

    def test_filter_list_anonymous(self):
        """Anonymous users should not be able to see surveys list view"""
        self.client.force_authenticate(user=None)
        response = self.client.get(_get_list_url(), {"user": self.admin_user.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Edit permissions
    def test_edit_admin(self):
        """Admin users should be able to edit surveys"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(_get_detail_url(1), self.survey_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_edit_regular(self):
        """Regular users should not be able to edit surveys"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.patch(_get_detail_url(1), self.survey_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_edit_attended(self):
        """Users who attended an event users should not be able to edit surveys"""
        self.client.force_authenticate(user=self.attended_user)
        response = self.client.patch(_get_detail_url(1), self.survey_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_edit_anonymous(self):
        """Anonymous users should not be able to edit surveys"""
        self.client.force_authenticate(user=None)
        response = self.client.patch(_get_detail_url(1), self.survey_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Edit cases
    def test_edit_survey_fields(self):
        """Regular survey fields should be updated properly"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(_get_detail_url(1), _test_surveys[0])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        actual = response.json()
        expected = _test_surveys[0]
        for key in ["title", "event", "activeFrom"]:
            self.assertEqual(actual[key], expected[key])

    def test_edit_questions(self):
        """Regular question fields should be updated properly, and then sending
        a new list of questions should remove and add questions as needed"""
        self.client.force_authenticate(user=self.admin_user)

        # First test updating the questions.
        response = self.client.patch(_get_detail_url(1), _test_surveys[1])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_questions = response.json()["questions"]
        self.assertEqual(len(response_questions), 3)
        self.compare_questions(response_questions, 1)

        # Then test that old questions get deleted when not included, and that new ones are added
        response = self.client.patch(_get_detail_url(1), _test_surveys[2])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_questions = response.json()["questions"]
        self.assertEqual(len(response_questions), 3)
        self.compare_questions(response_questions, 2)

    def compare_questions(self, questions, survey_id):
        for i, question in enumerate(questions):
            expected = _test_surveys[survey_id]["questions"][i]
            for key in [
                "id",
                "questionText",
                "questionType",
                "mandatory",
                "relativeIndex",
                "options",
            ]:
                if not (
                    key == "id" and key not in expected
                ):  # Because id is undefined for new questions
                    self.assertEqual(expected[key], question[key])

    def test_edit_options(self):
        """Regular option fields should be updated properly, and then sending
        a new list of options should remove and add questions as needed"""
        self.client.force_authenticate(user=self.admin_user)

        # First test updating the questions.
        response = self.client.patch(_get_detail_url(1), _test_surveys[3])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_options = response.json()["questions"][0]["options"]
        self.assertEqual(len(response_options), 2)
        self.compare_options(response_options, 3)

        # Then test that old questions get deleted when not included, and that new ones are added
        response = self.client.patch(_get_detail_url(1), _test_surveys[4])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_options = response.json()["questions"][0]["options"]
        self.assertEqual(len(response_options), 2)
        self.compare_options(response_options, 4)

    def compare_options(self, options, survey_id):
        for i, option in enumerate(options):
            expected = _test_surveys[survey_id]["questions"][0]["options"][i]
            for key in ["id", "optionText"]:
                if not (
                    key == "id" and key not in expected
                ):  # Because id is undefined for new questions
                    self.assertEqual(expected[key], option[key])

    def test_survey_results_without_token(self):
        """Test that trying to access the public survey results without a token fails"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(_get_list_url(), self.survey_data)
        survey = Survey.objects.get(id=response.json()["id"])

        self.client.force_authenticate(user=None)
        response = self.client.get(_get_token_url(survey.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_survey_results_with_token(self):
        """Test that you can access the public survey results with a token"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(_get_list_url(), self.survey_data)
        survey = Survey.objects.get(id=response.json()["id"])
        survey.generate_token()
        token = survey.token

        self.client.force_authenticate(user=None)
        header = {"HTTP_AUTHORIZATION": "Token {}".format(token)}
        response = self.client.get(_get_token_url(survey.id), {}, **header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json())

    def test_survey_results_data(self):
        """Test that you can access the public survey results with a token"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(_get_list_url(), self.survey_data)
        survey = Survey.objects.get(id=response.json()["id"])
        survey.generate_token()
        token = survey.token
        self.client.force_authenticate(user=None)
        header = {"HTTP_AUTHORIZATION": "Token {}".format(token)}
        response = self.client.get(_get_token_url(survey.id), {}, **header)

        self.assertEqual(response.json()["results"], survey.aggregate_submissions())
        self.assertEqual(response.json()["submissionCount"], survey.submissions.count())

    def test_survey_sharing(self):
        """Test that you can get a token for sharing an event"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(_get_list_url(), self.survey_data)
        self.assertFalse("token" in response.json())

        url = _get_detail_url(response.json()["id"]) + "share/"
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue(response.json())
        self.assertNotEqual(response.json()["token"], None)

    def test_survey_hiding(self):
        """Test that you can remove a token to unshare an event"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(_get_list_url(), self.survey_data)
        survey = Survey.objects.get(id=response.json()["id"])
        survey.generate_token()

        response = self.client.post(_get_detail_url(response.json()["id"]) + "hide/")
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue(response.json())
        self.assertEqual(response.json()["token"], None)

    def test_survey_export_admin(self):
        """Test that admins can export a survey as csv"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(_get_list_url(), self.survey_data)

        url = _get_detail_url(response.json()["id"]) + "csv/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_survey_export_admin_pdf(self):
        """Test that admins can export a survey as pdf"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(_get_list_url(), self.survey_data)

        url = _get_detail_url(response.json()["id"]) + "pdf/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_survey_export_regular(self):
        """Test that normal users can't export a survey as csv"""
        self.client.force_authenticate(user=self.attended_user)

        url = _get_detail_url(1) + "csv/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_survey_export_regular_pdf(self):
        """Test that normal users can't export a survey as pdf"""
        self.client.force_authenticate(user=self.attended_user)

        url = _get_detail_url(1) + "pdf/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_survey_export_admin_pdf_larger_survey(self):
        """Test that admins can export a survey as pdf"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            _get_list_url(),
            {"title": "Survey", "event": 5, "questions": _test_surveys[1]["questions"]},
        )

        url = _get_detail_url(response.json()["id"]) + "pdf/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
