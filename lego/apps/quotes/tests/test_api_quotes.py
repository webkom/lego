from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from lego.apps.quotes.models import Quote
from lego.apps.users.models import AbakusGroup, User


def _get_list_url():
    return reverse('api:v1:quote-list')


def _get_list_approved_url():
    return _get_list_url() + '?approved=True'


def _get_list_unapproved_url():
    return _get_list_url() + '?approved=False'


def _get_detail_url(pk):
    return reverse('api:v1:quote-detail', kwargs={'pk': pk})


def _get_approve_url(pk):
    return reverse('api:v1:quote-approve', kwargs={'pk': pk})


def _get_unapprove_url(pk):
    return reverse('api:v1:quote-unapprove', kwargs={'pk': pk})


class QuoteViewSetTestCase(APITestCase):
    fixtures = ['test_users.yaml', 'test_abakus_groups.yaml', 'test_quotes.yaml']

    def setUp(self):
        self.authenticated_user = User.objects.get(username='test1')
        self.group = AbakusGroup.objects.get(name='QuoteAdminTest')
        self.group.add_user(self.authenticated_user)
        self.unauthenticated_user = User.objects.get(username='test2')

        self.quote_data = {
            'title': 'QuoteTest',
            'text': 'TestText',
            'source': 'TestSource',
        }

    def test_create_authenticated(self):
        """Users with permissions should be able to create quotes"""
        self.client.force_authenticate(self.authenticated_user)
        response = self.client.post(_get_list_url(), self.quote_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_unauthenticated(self):
        """Users with no permissions should not be able to create quotes"""
        self.client.force_authenticate(self.unauthenticated_user)
        response = self.client.post(_get_list_url(), self.quote_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_authenticated(self):
        """Users with permissions should be able to list quotes"""
        self.client.force_authenticate(self.authenticated_user)
        response = self.client.get(_get_list_approved_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data)

    def test_list_unauthenticated(self):
        """Users with no permissions should not be able to list quotes"""
        self.client.force_authenticate(user=self.unauthenticated_user)
        response = self.client.get(_get_list_approved_url())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_approve_authenticated(self):
        """Users with permissions should be able to approve quotes"""
        self.client.force_authenticate(self.authenticated_user)
        response = self.client.put(_get_approve_url(3))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        quote = Quote.objects.get(id=3)
        self.assertTrue(quote.approved)

    def test_approve_unauthenticated(self):
        """Users with no permissions should not be able to approve quotes"""
        self.client.force_authenticate(self.unauthenticated_user)
        response = self.client.put(_get_approve_url(3))
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_unapproved_authenticated(self):
        """Users with permissions should be able to see unapproved quotes"""
        self.client.force_authenticate(self.authenticated_user)
        response = self.client.get(_get_list_unapproved_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        first_quote = response.data[0]
        self.assertFalse(first_quote['approved'])

    def test_list_unapproved_unauthenticated(self):
        """Users with no permissions should not be able to see unapproved quotes"""
        self.client.force_authenticate(self.authenticated_user)
        self.group.permissions = ['/sudo/admin/quotes/list/']
        self.group.save()

        response = self.client.get(_get_list_unapproved_url())
        self.assertFalse(response.data)
