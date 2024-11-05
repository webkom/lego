from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from lego.apps.meetings.models import MeetingTemplate
from lego.apps.users.models import AbakusGroup, User
from lego.utils.test_utils import BaseAPITestCase


def _get_template_list_url():
    return reverse("api:v1:meetingtemplate-list")


def _get_template_detail_url(pk):
    return reverse("api:v1:meetingtemplate-detail", kwargs={"pk": pk})


class MeetingTemplateTestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_users.yaml"]

    def setUp(self):
        self.user = User.objects.get(username="test2")
        self.other_user = User.objects.get(username="test1")
        self.group = AbakusGroup.objects.get(name="Webkom")
        self.group.add_user(self.user)
        self.client.force_authenticate(user=self.user)

    def test_create_template(self):
        """
        Test creating a new meeting template.
        """
        data = {
            "name": "Planning Meeting",
            "report": "<p>Plan report content</p>",
            "location": "Conference Room",
            "start_time": timezone.now(),
            "end_time": timezone.now() + timezone.timedelta(hours=1),
            "description": "Meeting to discuss project planning.",
            "mazemap_poi": 123,
            "report_author": self.user.id,
            "invited_users": [self.user.id],
            "invited_groups": [self.group.id],
        }
        response = self.client.post(_get_template_list_url(), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        template = MeetingTemplate.objects.get(name="Planning Meeting")
        self.assertEqual(template.created_by, self.user)
        self.assertEqual(template.location, "Conference Room")
        self.assertEqual(template.report_author.id, self.user.id)

    def test_create_duplicate_template_name_for_user(self):
        """
        Test that a user cannot create two templates with the same name.
        """
        data = {
            "name": "Weekly Sync",
            "report": "<p>Weekly updates</p>",
            "location": "Office",
            "start_time": timezone.now(),
            "end_time": timezone.now() + timezone.timedelta(hours=1),
        }
        self.client.post(_get_template_list_url(), data)
        response2 = self.client.post(_get_template_list_url(), data)
        self.assertEqual(response2.status_code, status.HTTP_409_CONFLICT)

    def test_retrieve_own_template(self):
        """
        Test retrieving a template that belongs to the authenticated user.
        """
        data = {
            "name": "Team Meeting",
            "report": "<p>Weekly updates</p>",
            "location": "Main Hall",
            "start_time": timezone.now(),
            "end_time": timezone.now() + timezone.timedelta(hours=1),
        }
        res = self.client.post(_get_template_list_url(), data)
        response = self.client.get(_get_template_detail_url(res.data["id"]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["name"], "Team Meeting")

    def test_retrieve_other_users_template(self):
        """
        Test that a user cannot retrieve another user's template.
        """
        other_template = MeetingTemplate.objects.create(
            name="Private Meeting",
            report="<p>Private content</p>",
            location="Private Room",
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=1),
            created_by=self.other_user,
        )
        response = self.client.get(_get_template_detail_url(other_template.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_own_template(self):
        """
        Test deleting a template that the user created.
        """
        data = {
            "name": "Team Meeting",
            "report": "<p>Weekly updates</p>",
            "location": "Conference Room",
            "start_time": timezone.now(),
            "end_time": timezone.now() + timezone.timedelta(hours=1),
        }
        res = self.client.post(_get_template_list_url(), data)
        response = self.client.delete(_get_template_detail_url(res.data["id"]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(MeetingTemplate.objects.filter(id=res.data["id"]).exists())

    def test_cannot_delete_other_users_template(self):
        """
        Test that a user cannot delete a template created by another user.
        """
        other_template = MeetingTemplate.objects.create(
            name="Another's Template",
            report="<p>Content</p>",
            location="Shared Space",
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=1),
            created_by=self.other_user,
        )
        response = self.client.delete(_get_template_detail_url(other_template.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
