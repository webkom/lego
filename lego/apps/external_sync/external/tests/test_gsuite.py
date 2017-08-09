from django.test import TestCase

from lego.apps.email.models import EmailAddress
from lego.apps.external_sync.external.gsuite import GSuiteSystem
from lego.apps.users.models import User


class GSuiteTestCase(TestCase):

    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml']

    def setUp(self):
        self.system = GSuiteSystem()

    def test_create_user(self):
        user = User.objects.create(
            username='haasyl',
            first_name='Håkon Martiniussen',
            last_name='Sylliaas',
            email='hakon@sylliaas.no',
        )
        email = EmailAddress.objects.create(email='hakons@abakus.no')
        user.internal_email = email
        user.save()

        self.system.delete_excess_users(User.objects.filter(username='haasyl'))
