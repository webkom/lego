from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase

from lego.apps.users.models import AbakusGroup, User

_test_quote_data = {
    'title': 'QuoteTest',
    'author': 1,
    'text': 'TestText',
    'source': 'TestSource',
    'start_time': '2011-09-01T13:20:30+03:00',
    'end_time': '2012-09-01T13:20:30+03:00',
    'merge_time': '2012-01-01T13:20:30+03:00',
}


def _get_list_url():
    return reverse('api:v1:quote-list')


def _get_list_approved_url():
    return _get_list_url() + '?approved=true'


def _get_list_unapproved_url():
    return _get_list_url() + '?approved=false'


def _get_detail_url(pk):
    return reverse('api:v1:quote-detail', kwargs={'pk': pk})


def _get_like_url(pk):
    return reverse('api:v1:quote-like', kwargs={'pk': pk})


def _get_unlike_url(pk):
    return reverse('api:v1:quote-unlike', kwargs={'pk': pk})


def _get_approve_url(pk):
    return reverse('api:v1:quote-approve', kwargs={'pk': pk})


def _get_unapprove_url(pk):
    return reverse('api:v1:quote-unapprove', kwargs={'pk': pk})


class ListApprovedQuotesTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_quotes.yaml', 'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_with_abakus_user(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.get(_get_list_approved_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_with_webkom_user(self):
        AbakusGroup.objects.get(name='Webkom').add_user(self.abakus_user)
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.get(_get_list_approved_url())
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


class RetrieveNonExistingQuoteTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_quotes.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_with_abakus_user(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.get(_get_detail_url(10))
        self.assertEqual(response.status_code, 404)


class RetrieveExistingQuoteTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_quotes.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_with_abakus_user(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.get(_get_detail_url(1))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 10)


class CreateQuoteTestCase(APITestCase):
    fixtures = ['test_users.yaml', 'initial_abakus_groups.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()
        AbakusGroup.objects.get(name='Webkom').add_user(self.abakus_user)

    def test_create(self):
        self.client.force_authenticate(self.abakus_user)
        response = self.client.post(_get_list_url(), _test_quote_data)
        self.assertEqual(response.status_code, 201)


class LikeApprovedQuoteTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_quotes.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_with_abakus_user(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.post(_get_like_url(1))
        self.assertEqual(response.status_code, 201)


class UnlikeApprovedQuoteTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_quotes.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_with_abakus_user(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.post(_get_unlike_url(2))
        self.assertEqual(response.status_code, 201)


class LikeUnapprovedQuoteTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_quotes.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_with_abakus_user(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.post(_get_like_url(3))
        # .get_object() raises a NotFound (404), raise Forbidden (403) instead?
        self.assertEqual(response.status_code, 404)

    def test_with_webkom_user(self):
        AbakusGroup.objects.get(name='Webkom').add_user(self.abakus_user)
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.post(_get_like_url(3))
        # TODO: Let admins like unapproved quotes
        self.assertEqual(response.status_code, 403)


class UnlikeUnapprovedQuoteTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_quotes.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_with_abakus_user(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.post(_get_unlike_url(3))
        # .get_object() raises a NotFound (404), raise Forbidden (403) instead?
        self.assertEqual(response.status_code, 404)

    def test_with_webkom_user(self):
        AbakusGroup.objects.get(name='Webkom').add_user(self.abakus_user)
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.post(_get_unlike_url(3))
        # TODO: Let admins unlike unapproved quotes
        self.assertEqual(response.status_code, 403)


class ApproveQuoteTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_quotes.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_with_abakus_user(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.put(_get_approve_url(3))
        self.assertEqual(response.status_code, 404)

    def test_with_webkom_user(self):
        AbakusGroup.objects.get(name='Webkom').add_user(self.abakus_user)
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.put(_get_approve_url(3))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 50)


class UnapproveQuoteTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_quotes.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_with_abakus_user(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.put(_get_unapprove_url(1))
        self.assertEqual(response.status_code, 403)

    def test_with_webkom_user(self):
        AbakusGroup.objects.get(name='Webkom').add_user(self.abakus_user)
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.put(_get_unapprove_url(1))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 10)
