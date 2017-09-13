from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase

from lego.apps.users.models import AbakusGroup, Membership, User


def _get_hest_detail_url(group_pk):
    return reverse('api:v1:membership-set-all-list', kwargs={'group_pk': group_pk})


class SetMembershipAPITestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml']

    def setUp(self):
        self.group = AbakusGroup.objects.get(name='Abakus')
        self.user = User.objects.get(username='pleb')
        self.group.add_user(self.user)
        webkom = AbakusGroup.objects.get(name='Webkom')
        self.webkommer = User.objects.get(username='webkommer')
        webkom.add_user(self.webkommer)

    def test_post_empty(self):
        self.client.force_authenticate(self.webkommer)
        before_count = Membership.objects.filter(abakus_group=self.group.pk).count()
        self.assertLess(0, before_count)
        res = self.client.post(_get_hest_detail_url(self.group.pk), {
            'memberships': []
        })
        self.assertEquals(res.status_code, 201)
        after_count = Membership.objects.filter(abakus_group=self.group.pk).count()
        self.assertEqual(0, after_count)

    def test_post_two_new(self):
        self.client.force_authenticate(self.webkommer)
        before_count = Membership.objects.filter(abakus_group=self.group.pk).count()
        self.assertLess(0, before_count)
        memberships = [{
            'user': User.objects.get(username='test1').pk,
            'role': 'member'
        }, {
            'user': User.objects.get(username='test2').pk,
        }]
        res = self.client.post(_get_hest_detail_url(self.group.pk), {
            'memberships': memberships
        })
        self.assertEquals(res.status_code, 201)
        after_count = Membership.objects.filter(abakus_group=self.group.pk).count()
        self.assertEqual(2, after_count)

    def test_post_with_existing(self):
        # self.user is already member of self.group
        self.client.force_authenticate(self.webkommer)
        before_count = Membership.objects.filter(abakus_group=self.group.pk).count()
        self.assertLess(0, before_count)
        memberships = [{
            'user': User.objects.get(username='test1').pk,
            'role': 'member'
        }, {
            'user': User.objects.get(username='test2').pk,
        }, {
            'user': self.user.pk,
            'role': 'leader'
        }]
        res = self.client.post(_get_hest_detail_url(self.group.pk), {
            'memberships': memberships
        })
        self.assertEquals(res.status_code, 201)
        after_count = Membership.objects.filter(abakus_group=self.group.pk).count()
        self.assertEqual(3, after_count)
        leader_memberships = Membership.objects.filter(abakus_group=self.group.pk, role='leader')
        self.assertEqual(leader_memberships.count(), 1)
        leader = leader_memberships[0].user
        self.assertEqual(leader, self.user)
