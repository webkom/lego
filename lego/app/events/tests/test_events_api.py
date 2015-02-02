from rest_framework.test import APITestCase

from lego.users.models import AbakusGroup, User


class ListEventsTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_events.yaml',
                'test_users.yaml']

    def setUp(self):
        self.all_users = User.objects.all()
        self.abakus_user = User.objects.filter(is_superuser=False).first()

        self.abakus_group = AbakusGroup.objects.get(name='Abakus')
        self.webkom_group = AbakusGroup.objects.get(name='Webkom')

    def test_with_abakus_user(self):
        self.abakus_group.add_user(self.abakus_user)
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.get('/api/v1/events/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_with_webkom_user(self):
        self.webkom_group.add_user(self.abakus_user)
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.get('/api/v1/events/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)


class RetrieveEventsTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_events.yaml',
                'test_users.yaml']

    def setUp(self):
        self.all_users = User.objects.all()
        self.abakus_user = User.objects.filter(is_superuser=False).first()

        self.abakus_group = AbakusGroup.objects.get(name='Abakus')
        self.abakus_group.add_user(self.abakus_user)

    def test_with_group_permission(self):
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.get('/api/v1/events/1/')
        self.assertEqual(response.status_code, 200)

    def test_without_group_permission(self):
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.get('/api/v1/events/2/')
        self.assertEqual(response.status_code, 404)
