from django.core.urlresolvers import reverse
from lego.app.quotes.serializers import QuoteCreateAndUpdateSerializer, QuoteLikeSerializer
from rest_framework.test import APITestCase

from lego.users.models import AbakusGroup, User

_test_quote_data = {
    'title': 'QuoteTest',
    'author': 1,
    'text': 'TestText',
    'source': 'TestSource',
    'start_time': '2011-09-01T13:20:30+03:00',
    'end_time': '2012-09-01T13:20:30+03:00',
    'merge_time': '2012-01-01T13:20:30+03:00',
}

_test_like_data = {
    'quote': 1,
    'user': 1
}


def _get_list_url():
    return reverse('quote-list')


def _get_list_unapproved_url():
    return reverse('quote-unapproved')


def _get_detail_url(pk):
    return reverse('quote-detail', kwargs={'pk': pk})


def _get_like_url(pk):
    return reverse('quote-like', kwargs={'pk': pk})


def _get_unlike_url(pk):
    return reverse('quote-unlike', kwargs={'pk': pk})


def _get_approve_url(pk):
    return reverse('quote-approve', kwargs={'pk': pk})


def _get_unapprove_url(pk):
    return reverse('quote-unapprove', kwargs={'pk': pk})



class ListApprovedQuotesTestCase(APITestCase):
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
        self.assertEqual(len(response.data), 2)


class ListUnapprovedQuotesTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_quotes.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_with_abakus_user(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.get(_get_list_unapproved_url())
        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(response.data), 1)

    def test_with_webkom_user(self):
        AbakusGroup.objects.get(name='Webkom').add_user(self.abakus_user)
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.get(_get_list_unapproved_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)


class CreateQuoteTestCase(APITestCase):
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


class LikeQuoteTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_quotes.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_with_abakus_user(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.post(_get_like_url(1))
        # TODO: use correct serializer
        test = QuoteLikeSerializer(data=_test_like_data)
        if not test.is_valid():
            print(test.errors)
        self.assertEqual(response.status_code, 201)


class UnlikeQuoteTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_quotes.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_with_abakus_user(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.post(_get_unlike_url(1))
        # TODO: use correct serializer
        test = QuoteLikeSerializer(data=_test_like_data)
        if not test.is_valid():
            print(test.errors)
        self.assertEqual(response.status_code, 201)
