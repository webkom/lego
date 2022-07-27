from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from lego.apps.surveys.models import Submission
from lego.apps.users.models import AbakusGroup, User


def _get_list_url(survey_pk):
    return reverse("api:v1:submission-list", kwargs={"survey_pk": survey_pk})


def _get_detail_url(survey_pk, submission_pk):
    return reverse(
        "api:v1:submission-detail", kwargs={"survey_pk": survey_pk, "pk": submission_pk}
    )


_answers = [
    {"question": 1, "submission": 1, "selectedOptions": [1], "answerText": ""},
    {"question": 2, "submission": 1, "selectedOptions": [3, 4, 5], "answerText": ""},
    {
        "question": 3,
        "submission": 1,
        "selectedOptions": [],
        "answerText": "Det var gøy",
    },
]


def submission_data(user, survey=1, include_answers=False):
    return {
        "user": user.id,
        "survey": survey,
        "answers": _answers if include_answers else [],
    }


class SubmissionViewSetTestCase(APITestCase):
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
        self.attended_user = User.objects.get(username="test1")
        self.attending_group = AbakusGroup.objects.get(name="Abakus")
        self.attending_group.add_user(self.attended_user)
        self.regular_user = User.objects.get(username="abakule")

    # Create
    def test_create_admin(self):
        """Admin users should be able to create submissions"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(_get_list_url(1), submission_data(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_attended(self):
        """Users who attended the event should be able to create submissions = answer the survey"""
        self.client.force_authenticate(user=self.attended_user)
        response = self.client.post(
            _get_list_url(1), submission_data(self.attended_user)
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_regular(self):
        """Regular users should not be able to create submissions"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post(
            _get_list_url(1), submission_data(self.regular_user)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Detail
    def test_detail_admin(self):
        """Admin users should be able to see detailed submissions"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(_get_detail_url(1, 1))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json())

    def test_detail_attended_own(self):
        """Users who attended the event should be able to see their own submission"""
        self.client.force_authenticate(user=self.attended_user)
        created = self.client.post(
            _get_list_url(1), submission_data(self.attended_user)
        )
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        response = self.client.get(_get_detail_url(1, created.json()["id"]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json())

    def test_detail_attended_other(self):
        """Users who attended the event should not be able to see other submissions"""
        self.client.force_authenticate(user=self.attended_user)
        response = self.client.get(_get_detail_url(1, 2))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_detail_regular(self):
        """Users should not be able see detailed submissions"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(_get_detail_url(1, 1))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Check if user has answered survey
    def test_answered_admin(self):
        """Admin users should be able to check if they have answered a survey"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(
            _get_list_url(1) + "?user=" + str(self.admin_user.id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json())

    def test_answered_attended_other(self):
        """Users who attended the event should be able to check if they have answered a survey"""
        self.client.force_authenticate(user=self.attended_user)
        response = self.client.get(
            _get_list_url(1) + "?user=" + str(self.attended_user.id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json())
        self.assertFalse(response.json().get("results", False))

        self.client.post(_get_list_url(1), submission_data(self.attended_user))
        response = self.client.get(
            _get_list_url(1) + "?user=" + str(self.attended_user.id)
        )
        self.assertTrue(response.json().get("results", False))

    def test_answered_regular(self):
        """Users should not be able to check if they have answered a survey if they haven't
        attended the event"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(
            _get_list_url(1) + "?user=" + str(self.regular_user.id)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # List
    def test_list_admin(self):
        """Users with permissions should be able to see submissions list view"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(_get_list_url(1))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_attended(self):
        """Users who attended the event should not be able to see list view"""
        self.client.force_authenticate(user=self.attended_user)
        response = self.client.get(_get_list_url(1))
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_list_regular(self):
        """Regular users should not be able to see submissions list view"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(_get_list_url(1))
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    # Edit
    def test_edit_admin(self):
        """Not even Admin users should be able to edit submissions"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(
            _get_detail_url(1, 1), submission_data(self.admin_user)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_edit_regular(self):
        """Regular users should not be able to edit submissions"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.patch(
            _get_detail_url(1, 1), submission_data(self.regular_user)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_edit_attended(self):
        """Users who attended an event users should not be able to edit submissions"""
        self.client.force_authenticate(user=self.attended_user)
        response = self.client.patch(
            _get_detail_url(1, 1), submission_data(self.attended_user)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Create
    def test_create_answer(self):
        """Check that every field is created successfully"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            _get_list_url(1), submission_data(self.admin_user, 1, True)
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        expected = submission_data(self.admin_user, 1)
        result = response.json()
        self.assertEqual(expected["user"], result["user"].get("id", None))

        self.assertEqual(len(result["answers"]), 3)
        for i, answer in enumerate(result["answers"]):
            expected = _answers[i]
            self.assertEqual(expected["question"], answer["question"].get("id", None))
            for key in ["answerText", "selectedOptions"]:
                self.assertEqual(expected[key], answer[key])

    # Hide
    def test_hide_admin(self):
        """Calling the hide() endpoint should successfully set hide_from_public"""
        self.client.force_authenticate(user=self.admin_user)
        answer_pk = 3
        submission = Submission.objects.get(pk=1)
        answer = submission.answers.get(pk=answer_pk)
        self.assertFalse(answer.hide_from_public)

        response = self.client.post(
            _get_detail_url(1, 1) + "hide/?answer=" + str(answer_pk)
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        response = self.client.get(_get_detail_url(1, 1))
        self.assertTrue(response.json())
        response_answers = response.json()["answers"]
        answer = next(x for x in response_answers if x["id"] == answer_pk)
        self.assertTrue("hideFromPublic" in answer)
        self.assertTrue(answer["hideFromPublic"])

    def test_show_admin(self):
        """Calling the show() endpoint should successfully set hide_from_public"""
        self.client.force_authenticate(user=self.admin_user)
        answer_pk = 3
        submission = Submission.objects.get(pk=1)
        answer = submission.answers.get(pk=answer_pk)
        answer.hide()

        response = self.client.post(
            _get_detail_url(1, 1) + "show/?answer=" + str(answer_pk)
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        response = self.client.get(_get_detail_url(1, 1))
        self.assertTrue(response.json())
        response_answers = response.json()["answers"]
        answer = next(x for x in response_answers if x["id"] == answer_pk)
        self.assertTrue("hideFromPublic" in answer)
        self.assertFalse(answer["hideFromPublic"])

    def test_hide_attended(self):
        """Attended users should not be able to hide or show answers"""
        self.client.force_authenticate(user=self.attended_user)
        response = self.client.post(_get_detail_url(1, 1) + "hide/?answer=3")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.post(_get_detail_url(1, 1) + "show/?answer=3")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_hide_regular(self):
        """Regular users should not be able to hide or show answers"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post(_get_detail_url(1, 1) + "hide/?answer=3")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.post(_get_detail_url(1, 1) + "show/?answer=3")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_hide_own(self):
        """Even whoever made the answer should not be able to hide or show answers"""
        submission = Submission.objects.get(pk=1)
        creator = submission.created_by
        self.client.force_authenticate(user=creator)
        response = self.client.post(_get_detail_url(1, 1) + "hide/?answer=3")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.post(_get_detail_url(1, 1) + "show/?answer=3")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_hide_without_answer(self):
        """Calling the hide() endpoint without an answer query param shouldn't work"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(_get_detail_url(1, 1) + "hide/")
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_hide_with_invalid_answer(self):
        """Calling the hide() endpoint with an incorrect answer pk should be 404"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(_get_detail_url(1, 1) + "hide/?answer=123")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
