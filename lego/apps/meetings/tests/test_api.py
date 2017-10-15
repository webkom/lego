from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase

from lego.apps.meetings import constants
from lego.apps.meetings.models import Meeting
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
    fixtures = ['test_abakus_groups.yaml', 'test_meetings.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakommer = User.objects.get(username='abakommer')
        AbakusGroup.objects.get(name='Abakom').add_user(self.abakommer)
        self.pleb = User.objects.get(username='pleb')

    def test_meeting_create(self):
        """
        All Abakus users should be able to create a meeting
        """
        self.client.force_authenticate(user=self.abakommer)
        res = self.client.post(_get_list_url(), test_meeting_data[0])
        self.assertEqual(res.status_code, 201)

    def test_pleb_cannot_create(self):
        self.client.force_authenticate(user=self.pleb)
        res = self.client.post(_get_list_url(), test_meeting_data[0])
        self.assertEqual(res.status_code, 403)


class RetrieveMeetingTestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_meetings.yaml',
                'test_users.yaml']

    def setUp(self):
        self.meeting = Meeting.objects.get(id=1)
        self.meeting2 = Meeting.objects.get(id=2)
        self.abakommer = User.objects.get(username='abakommer')
        AbakusGroup.objects.get(name='Abakom').add_user(self.abakommer)
        self.abakule = User.objects.get(username='test1')
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakule)
        self.pleb = User.objects.get(username='pleb')

    def test_participant_can_retrieve(self):
        invited = self.abakommer
        self.meeting.invite_user(invited)
        self.client.force_authenticate(invited)
        res = self.client.get(_get_detail_url(self.meeting.id))
        self.assertEqual(res.status_code, 200)

    def test_uninvited_cannot_retrieve(self):
        user = self.abakule
        self.client.force_authenticate(user)
        self.meeting.invite_user(user)
        self.meeting.uninvite_user(user)
        res = self.client.get(_get_detail_url(self.meeting.pk))
        self.assertTrue(res.status_code, 403)

    def test_pleb_cannot_retrieve(self):
        self.client.force_authenticate(self.pleb)
        res = self.client.get(_get_detail_url(self.meeting.id))
        self.assertEqual(res.status_code, 404)

    def test_can_see_invitations(self):
        self.meeting.created_by = self.abakule
        self.meeting.save()
        self.client.force_authenticate(self.abakule)

        self.meeting.invite_user(self.abakommer)
        self.meeting.invite_user(self.abakule)[0].accept()
        self.meeting.invite_user(self.pleb)[0].accept()

        self.meeting2.invite_user(self.pleb)

        for user in [self.abakule, self.abakommer, self.pleb]:
            self.client.force_authenticate(user)
            res = self.client.get(_get_invitations_list_url(self.meeting.id))
            self.assertEqual(res.status_code, 200)
            invitations = list(res.data['results'])
            attending = [inv for inv in invitations if inv['status'] == constants.ATTENDING]
            self.assertEqual(len(attending), 2)
            no_answer = [inv for inv in invitations if inv['status'] == constants.NO_ANSWER]
            self.assertEqual(len(no_answer), 1)


class DeleteMeetingTestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_meetings.yaml',
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

        self.client.force_authenticate(self.abakommer)
        res = self.client.delete(_get_detail_url(self.meeting.pk))
        self.assertEqual(res.status_code, 204)

    def test_cannot_delete_when_invited(self):
        self.meeting.invite_user(self.abakommer)
        self.client.force_authenticate(self.abakommer)
        res = self.client.delete(_get_detail_url(self.meeting.pk))
        self.assertEqual(res.status_code, 403)

    def test_cannot_delete_random_meeting(self):
        self.client.force_authenticate(self.abakommer)
        res = self.client.delete(_get_detail_url(self.meeting.pk))
        self.assertEqual(res.status_code, 404)


class InviteToMeetingTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'development_abakus_groups.yaml',
                'test_meetings.yaml', 'test_users.yaml', 'initial_files.yaml']

    def setUp(self):
        self.meeting = Meeting.objects.get(id=3)
        self.abakommer = User.objects.get(username='abakommer')
        AbakusGroup.objects.get(name='Abakom').add_user(self.abakommer)
        self.abakule = User.objects.get(username='test1')
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakule)
        self.pleb = User.objects.get(username='pleb')
        self.AbaBrygg = AbakusGroup.objects.get(name='AbaBrygg')

    def test_can_invite_to_own_meeting(self):
        self.meeting.created_by = self.abakommer
        self.meeting.save()

        self.client.force_authenticate(self.abakommer)
        res = self.client.post(_get_detail_url(self.meeting.id) + 'invite_user/', {
            'user': self.abakule.id,
        })
        self.assertEqual(res.status_code, 200)

    def test_member_can_invite_to_meeting(self):
        self.meeting.created_by = self.abakule
        self.meeting.save()

        me = self.abakommer
        self.meeting.invite_user(me)

        self.client.force_authenticate(me)
        res = self.client.post(_get_detail_url(self.meeting.id) + 'invite_user/', {
            'user': self.pleb.id,
        })
        self.assertEqual(res.status_code, 200)

    def test_abakulemember_can_invite_to_meeting(self):
        self.meeting.created_by = self.abakommer
        self.meeting.save()

        me = self.abakule
        self.meeting.invite_user(me)

        self.client.force_authenticate(me)
        res = self.client.post(_get_detail_url(self.meeting.id) + 'invite_user/', {
            'user': self.pleb.id,
        })
        self.assertEqual(res.status_code, 200)

    def test_can_bulk_invite_to_meeting(self):
        self.meeting.created_by = self.abakommer
        self.meeting.save()

        me = self.abakule
        self.meeting.invite_user(me)

        self.client.force_authenticate(me)
        res = self.client.post(_get_detail_url(self.meeting.id) + 'bulk_invite/', {
            'groups': [self.AbaBrygg.id],
            'users': [self.pleb.id]
        })
        self.assertEqual(res.status_code, 200)
        for user in self.AbaBrygg.users.all():
            present = self.meeting.invited_users.filter(id=user.id).exists()
            self.assertTrue(present)
        self.assertTrue(self.meeting.invited_users.filter(id=self.pleb.id))

    def test_can_not_bulk_invite_to_unknown_meeting(self):
        me = self.abakommer
        self.client.force_authenticate(me)
        res = self.client.post(_get_detail_url(self.meeting.id) + 'bulk_invite/', {
            'groups': [self.AbaBrygg.id],
            'users': [self.pleb.id]
        })
        self.assertEqual(res.status_code, 404)
        for user in self.AbaBrygg.users.all():
            present = self.meeting.invited_users.filter(id=user.id).exists()
            self.assertFalse(present)
        self.assertFalse(self.meeting.invited_users.filter(id=self.pleb.id))

    def test_can_not_invite_to_unknown_meeting(self):
        me = self.abakommer
        self.client.force_authenticate(me)
        res = self.client.post(_get_invitations_list_url(self.meeting.id), {
            'user': self.abakule.id,
        })
        self.assertEqual(res.status_code, 403)

    def test_can_invite_group(self):
        me = self.abakommer
        self.meeting.created_by = me
        self.meeting.save()
        self.client.force_authenticate(me)
        webkom = AbakusGroup.objects.get(name='Webkom')
        res = self.client.post(_get_detail_url(self.meeting.id) + 'invite_group/', {
            'group': webkom.id
        })
        self.assertEqual(res.status_code, 200)
        for user in webkom.users.all():
            present = self.meeting.invited_users.filter(id=user.id).exists()
            self.assertTrue(present)


class UpdateInviteTestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_meetings.yaml',
                'test_users.yaml']

    def setUp(self):
        self.meeting = Meeting.objects.get(id=3)
        self.abakommer = User.objects.get(username='abakommer')
        AbakusGroup.objects.get(name='Abakom').add_user(self.abakommer)
        self.abakule = User.objects.get(username='test1')
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakule)
        self.pleb = User.objects.get(username='pleb')

    def test_can_update_own_status(self):
        me = self.abakommer

        invite = self.meeting.invite_user(me)[0]
        self.assertEqual(invite.status, constants.NO_ANSWER)
        self.client.force_authenticate(me)
        res = self.client.patch(_get_invitations_list_url(self.meeting.id) + str(me.id) + '/', {
            'status': constants.ATTENDING
        })
        self.assertEqual(res.status_code, 200)
        invite.refresh_from_db()
        self.assertEqual(invite.status, constants.ATTENDING)

    def test_cannot_update_other_status(self):
        me = self.abakommer
        other = self.pleb

        self.meeting.invite_user(other)
        invite = self.meeting.invite_user(me)[0]
        self.assertEqual(invite.status, constants.NO_ANSWER)
        self.client.force_authenticate(other)
        res = self.client.patch(_get_invitations_list_url(self.meeting.id) + str(me.id) + '/', {
            'status': constants.ATTENDING
        })
        self.assertEqual(res.status_code, 403)
        invite.refresh_from_db()
        self.assertEqual(invite.status, constants.NO_ANSWER)

    def test_cannot_update_to_other_user(self):
        me = self.abakule
        invite = self.meeting.invite_user(me)[0]
        self.client.force_authenticate(me)
        self.client.patch(_get_invitations_list_url(self.meeting.id) + str(me.id) + '/', {
            'user': self.pleb.id
        })
        invite.refresh_from_db()
        self.assertEqual(invite.user, me)


class UnauthorizedTestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_meetings.yaml',
                'test_users.yaml']

    def setUp(self):
        self.meeting = Meeting.objects.get(id=3)

    def test_can_not_retrieve_list(self):
        res = self.client.get(_get_list_url())
        self.assertEqual(res.status_code, 401)

    def test_can_not_retrieve_meeting(self):
        res = self.client.get(_get_detail_url(self.meeting.id))
        self.assertEqual(res.status_code, 401)
