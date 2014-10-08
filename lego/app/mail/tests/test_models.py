from basis.models import BasisModel
from django.test import TestCase
from django.contrib.auth.models import User

from ..models import GenericMappingMixin, GenericMapping


class GenericModelTest(BasisModel, GenericMappingMixin):
    """
    This class is a example class used for testing the generic mail mapping.
    This is typically a class like the Event or Group class
    """
    def get_mail_recipients(self):
        return User.objects.all()


class ModelsTestCase(TestCase):
    def setUp(self):
        user1 = User(username='user1', email='user1@abakus.no')
        user1.save()

        user2 = User(username='user2', email='user2@abakus.no')
        user2.save()

    def test_generic_mappings_recipients_list(self):
        genericModelTest = GenericModelTest()
        genericModelTest.save()
        genericMapping1 = GenericMapping(content_object=genericModelTest)
        genericMapping1.save()
        self.assertEqual(genericMapping1.get_recipients(), ['user1@abakus.no', 'user2@abakus.no'])

