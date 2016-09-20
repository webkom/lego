from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase

from lego.apps.meetings.models import Meeting
from lego.apps.users.models import User, AbakusGroup


test_meeting_data = [
    {
        'title': 'Halla damer',
        'location': 'Plebkom',
        'start_time': '2016-10-01T13:20:30Z',
        'end_time': '2016-10-01T14:00:30Z',
    }
]


def _get_list_url():
    return reverse('api:v1:meeting-list')


def _get_detail_url(pk):
    return reverse('api:v1:meeting-detail', kwargs={'pk': pk})


class CreateMeetingTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'development_meetings.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakom_user = User.objects.get(id=1)
        AbakusGroup.objects.get(name='Webkom').add_user(self.abakom_user)

        self.pleb = User.objects.get(username='not_abakommer')
        AbakusGroup.objects.get(name='Abakus').add_user(self.pleb)

    def test_meeting_create(self):
        """
        All Abakom users should be able to create a meeting
        """
        self.client.force_authenticate(user=self.abakom_user)
        res = self.client.post(_get_list_url(), test_meeting_data[0])
        self.assertEqual(res.status_code, 201)

    def test_pleb_cannot_create(self):
        """
        Regular Abakus members cannot create a meeting
        """
        self.client.force_authenticate(self.pleb)
        res = self.client.post(_get_list_url(), test_meeting_data[0])
        self.assertEqual(res.status_code, 403)


class RetrieveMeetingTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'development_meetings.yaml',
                'test_users.yaml']

    def setUp(self):
        self.meeting = Meeting.objects.get(id=1)
        AbakusGroup.objects.get(name='readme').add_user(self.meeting.author)
        self.pleb = User.objects.get(username='not_abakommer')
        AbakusGroup.objects.get(name='Abakus').add_user(self.pleb)

    def test_author_can_retrieve(self):
        self.client.force_authenticate(self.meeting.author)
        res = self.client.get(_get_detail_url(self.meeting.id))
        self.assertEqual(res.status_code, 200)

    def test_dude_cannot_retrieve(self):
        self.client.force_authenticate(self.pleb)
        res = self.client.get(_get_detail_url(self.meeting.id))
        self.assertEqual(res.status_code, 404)
