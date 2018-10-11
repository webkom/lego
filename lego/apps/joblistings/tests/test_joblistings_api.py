from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from lego.apps.joblistings.models import Joblisting
from lego.apps.users.models import AbakusGroup, User
from lego.utils.test_utils import BaseAPITestCase

_test_joblistings_data = [
    {
        'title': 'BEKK - sommerjobb 2017',
        'company': 1,
        'description': 'En bedrift.',
        'text': 'Text',
        'deadline': '2017-11-03T02:00:00+00:00',
        'visible_from': '2016-09-30T16:15:00+00:00',
        'visible_to': '2017-09-30T16:15:00+00:00',
        'job_type': 'summer_job',
        'from_year': 3,
        'to_year': 5,
        'application_url': 'http://www.vg.no',
        'workplaces': [{
            'town': 'Oslo'
        }]
    },
    {
        'title': 'EY',
        'company': 2,
        'description': 'En bedrift.',
        'text': 'Text2',
        'deadline': '2017-11-03T02:00:00+00:00',
        'visible_from': '2016-09-30T16:15:00+00:00',
        'visible_to': '2017-09-30T16:15:00+00:00',
        'job_type': 'summer_job',
        'from_year': 3,
        'to_year': 5,
        'application_url': 'http://www.vg.no',
        'workplaces': [{
            'town': 'Trondheim'
        }]
    },
    {
        'title': 'Itera',
        'company': 1,
        'description': 'En bedrift.',
        'text': 'Text3',
        'deadline': '2017-11-03T02:00:00+00:00',
        'visible_from': '2016-09-30T16:15:00+00:00',
        'visible_to': '2017-09-30T16:15:00+00:00',
        'job_type': 'summer_job',
        'from_year': 3,
        'to_year': 5,
        'application_url': 'http://www.vg.no',
        'workplaces': [{
            'town': 'Oslo'
        }, {
            'town': 'Trondheim'
        }]
    }
]


def _get_list_url():
    return reverse('api:v1:joblisting-list')


def _get_detail_url(pk):
    return reverse('api:v1:joblisting-detail', kwargs={'pk': pk})


class ListJoblistingsTestCase(BaseAPITestCase):
    fixtures = [
        'development_joblistings.yaml', 'test_users.yaml', 'development_companies.yaml',
        'test_abakus_groups.yaml'
    ]

    def setUp(self):
        self.abakus_user = User.objects.all().first()
        now = timezone.now()
        Joblisting.objects.all().update(
            visible_from=now - timedelta(days=10), visible_to=now + timedelta(days=10)
        )

        Joblisting.objects.filter(
            pk=3
        ).update(visible_from=now - timedelta(days=10), visible_to=now - timedelta(days=5))

    def test_with_abakus_user(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        joblisting_response = self.client.get(_get_list_url())
        self.assertEqual(joblisting_response.status_code, 200)
        self.assertEqual(len(joblisting_response.data['results']), 3)

    def test_without_user(self):
        joblisting_response = self.client.get(_get_list_url())
        self.assertEqual(joblisting_response.status_code, 200)
        self.assertEqual(len(joblisting_response.data['results']), 3)

    def test_list_after_visible_to(self):
        joblisting = Joblisting.objects.all().first()
        joblisting.visible_to = timezone.now() - timedelta(days=2)
        joblisting.save()
        joblisting_response = self.client.get(_get_list_url())
        self.assertEqual(joblisting_response.status_code, 200)
        self.assertEqual(len(joblisting_response.data['results']), 2)


class RetrieveJoblistingsTestCase(BaseAPITestCase):
    fixtures = [
        'development_joblistings.yaml', 'test_users.yaml', 'development_companies.yaml',
        'test_abakus_groups.yaml'
    ]

    def setUp(self):
        self.abakus_user = User.objects.all().first()
        now = timezone.now()
        Joblisting.objects.all().update(
            visible_from=now - timedelta(days=10), visible_to=now + timedelta(days=10)
        )

        Joblisting.objects.filter(
            pk=3
        ).update(visible_from=now - timedelta(days=10), visible_to=now - timedelta(days=5))

    def test_with_group_permission(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        joblisting_response = self.client.get(_get_detail_url(1))
        self.assertEqual(joblisting_response.data['id'], 1)
        self.assertEqual(joblisting_response.status_code, 200)

    def test_without_group_permission(self):
        self.client.force_authenticate(self.abakus_user)
        joblisting_response = self.client.get(_get_detail_url(2))
        self.assertEqual(joblisting_response.data['id'], 2)
        self.assertEqual(joblisting_response.status_code, 200)


class CreateJoblistingsTestCase(BaseAPITestCase):
    fixtures = [
        'development_joblistings.yaml', 'test_users.yaml', 'development_companies.yaml',
        'test_abakus_groups.yaml'
    ]

    def setUp(self):
        self.abakom_user = User.objects.get(username='abakommer')
        AbakusGroup.objects.get(name='Abakom').add_user(self.abakom_user)
        self.not_abakom_user = User.objects.get(username='pleb')
        now = timezone.now()
        Joblisting.objects.all().update(
            visible_from=now - timedelta(days=10), visible_to=now + timedelta(days=10)
        )

        Joblisting.objects.filter(
            pk=3
        ).update(visible_from=now - timedelta(days=10), visible_to=now - timedelta(days=5))

    def test_joblistings_create(self):
        self.client.force_authenticate(user=self.abakom_user)
        res = self.client.post(_get_list_url(), _test_joblistings_data[0])
        self.assertEqual(res.status_code, 201)

    def test_pleb_cannot_create(self):
        self.client.force_authenticate(user=self.not_abakom_user)
        res = self.client.post(_get_list_url(), _test_joblistings_data[0])
        self.assertEqual(res.status_code, 403)


class EditJoblistingsTestCase(BaseAPITestCase):
    fixtures = [
        'development_joblistings.yaml', 'test_users.yaml', 'development_companies.yaml',
        'test_abakus_groups.yaml'
    ]

    def setUp(self):
        self.abakom_user = User.objects.get(username='abakommer')
        AbakusGroup.objects.get(name='Abakom').add_user(self.abakom_user)
        self.not_abakom_user = User.objects.get(username='pleb')

        now = timezone.now()
        Joblisting.objects.all().update(
            visible_from=now - timedelta(days=10), visible_to=now + timedelta(days=10)
        )

        Joblisting.objects.filter(
            pk=3
        ).update(visible_from=now - timedelta(days=10), visible_to=now - timedelta(days=5))

    def test_joblistings_edit_one_workplace(self):
        self.client.force_authenticate(user=self.abakom_user)
        res = self.client.put(_get_detail_url(1), _test_joblistings_data[1])
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data.get('workplaces')[0].get('town'), 'Trondheim')

    def test_joblistings_edit_multiple_workplace(self):
        self.client.force_authenticate(user=self.abakom_user)
        res = self.client.put(_get_detail_url(1), _test_joblistings_data[2])
        self.assertEqual(res.status_code, 200)
        self.assertEqual('Itera', res.data.get('title'))
        self.assertEqual(len(res.data.get('workplaces')), 2)

    def test_pleb_cannot_edit(self):
        self.client.force_authenticate(user=self.not_abakom_user)
        res = self.client.put(_get_detail_url(1), _test_joblistings_data[1])
        self.assertEqual(res.status_code, 403)


class DeleteJoblistingsTestCase(BaseAPITestCase):
    fixtures = [
        'development_joblistings.yaml', 'test_users.yaml', 'development_companies.yaml',
        'test_abakus_groups.yaml'
    ]

    def setUp(self):
        self.joblisting = Joblisting.objects.get(id=1)
        self.abakom_user = User.objects.get(username='abakommer')
        AbakusGroup.objects.get(name='Abakom').add_user(self.abakom_user)
        self.not_abakom_user = User.objects.get(username='pleb')
        AbakusGroup.objects.get(name='Abakus').add_user(self.not_abakom_user)
        now = timezone.now()
        Joblisting.objects.all().update(
            visible_from=now - timedelta(days=10), visible_to=now + timedelta(days=10)
        )

        Joblisting.objects.filter(
            pk=3
        ).update(visible_from=now - timedelta(days=10), visible_to=now - timedelta(days=5))

    def test_can_delete(self):
        self.client.force_authenticate(self.abakom_user)
        res = self.client.delete(_get_detail_url(self.joblisting.pk))
        self.assertEqual(res.status_code, 204)

    def test_cannot_delete(self):
        self.client.force_authenticate(self.not_abakom_user)
        res = self.client.delete(_get_detail_url(self.joblisting.pk))
        self.assertEqual(res.status_code, 403)
