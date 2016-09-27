from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase

from lego.apps.meetings.models import Meeting, MeetingInvitation
from lego.apps.users.models import AbakusGroup, User

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


def _get_invitations_list_url(pk):
    return reverse('api:v1:meeting-invitations-list', kwargs={'meeting_pk': pk})


class CreateMeetingTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'development_meetings.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakom_user = User.objects.get(id=1)
        AbakusGroup.objects.get(name='Webkom').add_user(self.abakom_user)

        self.abakule = User.objects.get(username='abakule')
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakule)

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
        self.client.force_authenticate(self.abakule)
        res = self.client.post(_get_list_url(), test_meeting_data[0])
        self.assertEqual(res.status_code, 403)


class RetrieveMeetingTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'development_meetings.yaml',
                'test_users.yaml']

    def setUp(self):
        self.meeting = Meeting.objects.get(id=1)
        self.abakommer = User.objects.get(username='abakommer')
        AbakusGroup.objects.get(name='Abakom').add_user(self.abakommer)
        self.abakule = User.objects.get(username='test1')
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakule)
        self.pleb = User.objects.get(username='pleb')

    def test_participant_can_retrieve(self):
        invited = self.abakule
        self.client.force_authenticate(invited)
        self.meeting.invite(invited)
        res = self.client.get(_get_detail_url(self.meeting.id))
        self.assertEqual(res.status_code, 200)

    def test_uninvited_cannot_retrieve(self):
        user = self.abakule
        self.client.force_authenticate(user)
        self.meeting.invite(user)
        self.meeting.uninvite(user)
        res = self.client.get(_get_detail_url(self.meeting.pk))
        self.assertTrue(res.status_code >= 403)

    def test_pleb_cannot_retrieve(self):
        self.client.force_authenticate(self.pleb)
        res = self.client.get(_get_detail_url(self.meeting.id))
        self.assertTrue(res.status_code >= 403)

    def test_abakus_can_retrieve_abameeting(self):
        abameeting = Meeting.objects.get(title='Genvors')
        for user in [self.abakule, self.abakommer]:
            self.client.force_authenticate(user)
            res = self.client.get(_get_detail_url(abameeting.id))
            self.assertEqual(res.status_code, 200)

    def test_can_see_invitations(self):
        self.meeting.created_by = self.abakule
        self.meeting.save()
        self.client.force_authenticate(self.abakule)

        self.meeting.invite(self.abakommer)
        self.meeting.invite(self.abakule)[0].accept()
        self.meeting.invite(self.pleb)[0].accept()

        for user in [self.abakule, self.abakommer, self.pleb]:
            self.client.force_authenticate(user)
            res = self.client.get(_get_invitations_list_url(self.meeting.id))
            self.assertEqual(res.status_code, 200)
            invitations = list(res.data)
            attending = [inv for inv in invitations if inv['status'] == MeetingInvitation.ATTENDING]
            self.assertEqual(len(attending), 2)
            no_answer = [inv for inv in invitations if inv['status'] == MeetingInvitation.NO_ANSWER]
            self.assertEqual(len(no_answer), 1)


class DeleteMeetingTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'development_meetings.yaml',
                'test_users.yaml']

    def setUp(self):
        self.meeting = Meeting.objects.get(id=1)
        self.abakommer = User.objects.get(username='abakommer')
        AbakusGroup.objects.get(name='Abakom').add_user(self.abakommer)
        self.abakule = User.objects.get(username='test1')
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakule)
        self.pleb = User.objects.get(username='pleb')

    def test_can_delete_own_meeting(self):
        self.meeting.created_by = self.abakommer
        self.meeting.save()
        # This is done by default in MeetingSerializer.create
        self.meeting.invite(self.abakommer)

        self.client.force_authenticate(self.abakommer)
        res = self.client.delete(_get_detail_url(self.meeting.pk))
        self.assertEqual(res.status_code, 204)

    def test_cannot_delete_when_invited(self):
        self.meeting.invite(self.abakommer)
        self.client.force_authenticate(self.abakommer)
        res = self.client.delete(_get_detail_url(self.meeting.pk))
        self.assertEqual(res.status_code, 403)

    def test_cannot_delete_random_meeting(self):
        self.client.force_authenticate(self.abakommer)
        res = self.client.delete(_get_detail_url(self.meeting.pk))
        self.assertEqual(res.status_code, 403)


class InviteToMeetingTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'development_meetings.yaml',
                'test_users.yaml']

    def setUp(self):
        self.meeting = Meeting.objects.get(id=1)
        self.abakommer = User.objects.get(username='abakommer')
        AbakusGroup.objects.get(name='Abakom').add_user(self.abakommer)
        self.abakule = User.objects.get(username='test1')
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakule)
        self.pleb = User.objects.get(username='pleb')

    def test_can_invite_to_own_meeting(self):
        self.meeting.created_by = self.abakommer
        self.meeting.save()
        self.client.force_authenticate(self.abakommer)
        data = {
            'user': self.abakule.id,
        }
        res = self.client.post(_get_invitations_list_url(self.meeting.id), data)
        self.assertEqual(res.status_code, 201)

    def test_can_not_invite_to_unknown_meeting(self):
        me = self.abakommer
        self.client.force_authenticate(me)
        data = {
            'user': self.abakule.id,
        }
        res = self.client.post(_get_invitations_list_url(self.meeting.id), data)
        self.assertEqual(res.status_code, 403)
