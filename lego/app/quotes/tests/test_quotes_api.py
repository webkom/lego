from django.core.urlresolvers import reverse
from lego.app.quotes.serializers import QuoteCreateAndUpdateSerializer
from rest_framework.test import APITestCase

from lego.users.models import AbakusGroup, User

_test_quote_data = {
    'title': 'Event',
    'author': 1,
    'ingress': 'TestIngress',
    'text': 'TestText',
}

def _get_list_url():
    return reverse('event-list')


def _get_detail_url(pk):
    return reverse('event-detail', kwargs={'pk': pk})


class ListQuotesTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_quotes.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_with_abakus_user(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.get(_get_list_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_with_webkom_user(self):
        AbakusGroup.objects.get(name='Webkom').add_user(self.abakus_user)
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.get(_get_list_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)


class RetrieveQuotesTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_quotes.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_with_group_permission(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.get(_get_detail_url(1))
        self.assertEqual(response.status_code, 200)

    def test_without_group_permission(self):
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.get(_get_detail_url(2))
        self.assertEqual(response.status_code, 404)


class CreateQuotesTestCase(APITestCase):
    fixtures = ['test_users.yaml', 'initial_abakus_groups.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()
        AbakusGroup.objects.get(name='Webkom').add_user(self.abakus_user)

    def test_create(self):
        self.client.force_authenticate(self.abakus_user)
        response = self.client.post(_get_list_url(), _test_quote_data)
        test = QuoteCreateAndUpdateSerializer(data=_test_quote_data)
        if not test.is_valid():
            print(test.errors)
        self.assertEqual(response.status_code, 201)

    def test_pool_creation(self):
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.post(_get_list_url(), _test_quote_data)
        self.assertEqual(response.status_code, 201)