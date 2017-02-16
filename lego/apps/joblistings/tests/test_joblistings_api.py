from datetime import timedelta

from django.core.urlresolvers import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from lego.apps.joblistings.models import Joblisting
from lego.apps.users.models import AbakusGroup, User

_test_joblistings_data = [
    {
        'title': 'BEKK - sommerjobb 2017',
        'description': 'En bedrift.',
        'text': 'BEKK er et solid programvarehus i kraftig vekst. \
                 Vi er 245 dyktige medarbeidere, fordelt på hovedkontoret i Bodø og \
                 avdelingskontorer i Tromsø, Trondheim, Bergen og Oslo. Vi ønsker å \
                 effektivisere helsevesenet ved å lage en fantastisk elektronisk pasientjournal \
                 utviklet av dyktige utviklere i samarbeid med en erfaren medisinsk stab',
        'deadline': '2016-11-03T02:00:00+00:00',
        'visible_from': '2016-09-30T16:15:00+00:00',
        'visible_to': '2017-09-30T16:15:00+00:00',
        'job_type': 'summer_job',
        'from_year': 3,
        'to_year': 5,
    }
]

_test_company_data = [
    {
        'id': 1,
        'name': 'BEKK',
        'website': 'bekk.no',
    }
]

_test_workplaces_data = [
    {
        'town': 'Oslo',
    },
    {
        'town': 'Trondheim',
    },
    {
        'town': 'Bergen',
    }
]

_test_companycontact_data = [
    {
        'name': 'Abraham Finnsen',
        'mail': 'abraham@finnsen.no',
    }
]



def _get_list_url():
    return reverse('api:v1:joblisting-list')


def _get_detail_url(pk):
    return reverse('api:v1:joblisting-detail', kwargs={'pk': pk})


class ListJoblistingsTestCase(APITestCase):
    fixtures = ['development_joblistings.yaml', 'test_users.yaml',
                'development_companies.yaml', 'initial_abakus_groups.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

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


class RetrieveJoblistingsTestCase(APITestCase):
    fixtures = ['development_joblistings.yaml', 'test_users.yaml',
                'development_companies.yaml', 'initial_abakus_groups.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

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


class CreateJoblistingsTestCase(APITestCase):
    fixtures = ['development_joblistings.yaml', 'test_users.yaml',
                'development_companies.yaml', 'initial_abakus_groups.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()
        self.client.force_authenticate(self.abakus_user)

    def test_joblistings_creation(self):
