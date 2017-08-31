from rest_framework import status
from rest_framework.test import APITestCase

from lego.apps.email.models import EmailList
from lego.apps.users.models import AbakusGroup, User


class EmailListTestCase(APITestCase):

    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml',
                'test_email_addresses.yaml', 'test_email_lists.yaml']

    def setUp(self):
        self.url = '/api/v1/email-lists/'
        self.user = User.objects.get(username='test1')
        self.admin_group = AbakusGroup.objects.get(name='EmailAdminTest')
        self.admin_group.add_user(self.user)

        self.client.force_login(self.user)

    def test_list(self):
        """The list endpoint is available"""
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_create_list(self):
        """Create a new list with a new email"""
        response = self.client.post(self.url, {
            'name': 'Jubileum',
            'email': 'jubileum',
            'users': [
                1, 2
            ]
        })
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_create_list_invalid_email(self):
        """Bad request when the user tries to create a list with an invalid email"""
        response = self.client.post(self.url, {
            'name': 'Invalid',
            'email': 'not valid email',
            'users': [
                1, 2
            ]
        })
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        response = self.client.post(self.url, {
            'name': 'Invalid',
            'email': 'admin',
            'users': [
                1, 2
            ]
        })
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_change_assigned_email(self):
        """It is'nt possible to change the email after the list is created"""
        response = self.client.patch(f'{self.url}1/', {
            'email': 'changed'
        })
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        self.assertEquals('test', EmailList.objects.get(id=1).email_id)

    def test_delete_endpoint_not_available(self):
        """The delete endpoint is'nt available."""
        response = self.client.delete(f'{self.url}1/')
        self.assertEquals(status.HTTP_403_FORBIDDEN, response.status_code)


class UserEmailTestCase(APITestCase):

    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml',
                'test_email_addresses.yaml', 'test_email_lists.yaml']

    def setUp(self):
        self.url = '/api/v1/email-users/'
        self.user = User.objects.get(username='test1')
        self.admin_group = AbakusGroup.objects.get(name='EmailAdminTest')
        self.admin_group.add_user(self.user)

        self.client.force_login(self.user)

    def test_list(self):
        """The list endpoint is available"""
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_retrieve(self):
        """It is possible to retrieve the user"""
        response = self.client.get(f'{self.url}1/')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_set_email(self):
        """It is possible to change from no email to one nobody has used"""
        response = self.client.patch(f'{self.url}1/', {
            'internal_email': 'testgroup'
        })
        self.assertEquals(status.HTTP_200_OK, response.status_code)

    def test_set_email_to_none(self):
        """It is not possible to set the email mack to none"""
        User.objects.filter(id=1).update(internal_email='noassigned')

        response = self.client.patch(f'{self.url}1/', {
            'internal_email': None
        })
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_set_email_to_new(self):
        """
        It is not possible to change the email to a new one when you already gave an assigned email
        """
        User.objects.filter(id=1).update(internal_email='noassigned')

        response = self.client.patch(f'{self.url}1/', {
            'internal_email': 'unused'
        })
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_set_email_to_an_assigned(self):
        """It is not possible to use an email used by another instance"""
        response = self.client.patch(f'{self.url}1/', {
            'internal_email': 'test'
        })
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)


class GroupEmailTestCase(APITestCase):

    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml',
                'test_email_addresses.yaml', 'test_email_lists.yaml']

    def setUp(self):
        self.url = '/api/v1/email-groups/'
        self.user = User.objects.get(username='test1')
        self.admin_group = AbakusGroup.objects.get(name='EmailAdminTest')
        self.admin_group.add_user(self.user)

        self.client.force_login(self.user)

    def test_list(self):
        """The list endpoint is available"""
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_retrieve(self):
        """It is possible to retrieve the group"""
        response = self.client.get(f'{self.url}1/')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_set_email(self):
        """It is possible to change from no email to one nobody has used"""
        response = self.client.patch(f'{self.url}1/', {
            'internal_email': 'testgroup'
        })
        self.assertEquals(status.HTTP_200_OK, response.status_code)

    def test_set_email_to_none(self):
        """It is not possible to set the email mack to none"""
        AbakusGroup.objects.filter(id=1).update(internal_email='noassigned')

        response = self.client.patch(f'{self.url}1/', {
            'internal_email': None
        })
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_set_email_to_new(self):
        """
        It is not possible to change the email to a new one when you already gave an assigned email
        """
        AbakusGroup.objects.filter(id=1).update(internal_email='noassigned')

        response = self.client.patch(f'{self.url}1/', {
            'internal_email': 'unused'
        })
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_set_email_to_an_assigned(self):
        """It is not possible to use an email used by another instance"""
        response = self.client.patch(f'{self.url}1/', {
            'internal_email': 'test'
        })
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
