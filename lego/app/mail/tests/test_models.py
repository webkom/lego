# -*- coding: utf8 -*-
from basis.models import BasisModel
from django.test import TestCase
from django.db import models
from django.contrib.auth.models import User

from lego.app.mail.models import GenericMappingMixin, GenericMapping


class GenericModelTest(BasisModel, GenericMappingMixin):
    """
    This class is a example class used for testing the generic mail mapping.
    This is typically a class like the Event or Group class
    """
    empty_queryset = models.NullBooleanField()

    def get_mail_recipients(self):
        if self.empty_queryset is None:
            return TestCase()  # Just return some shit..
        elif self.empty_queryset:
            return User.objects.filter(username='abakus')  # Empty queryset
        else:
            return User.objects.all()


class ModelsTestCase(TestCase):
    def setUp(self):
        user1 = User(username='user1', email='user1@abakus.no')
        user1.save()

        user2 = User(username='user2', email='user2@abakus.no')
        user2.save()

    def test_generic_mappings_recipients_list_valid_queryset(self):
        generic_model_test = GenericModelTest(empty_queryset=False)
        generic_model_test.save()
        generic_mapping = GenericMapping(content_object=generic_model_test)
        generic_mapping.save()
        self.assertEqual(generic_mapping.get_recipients(), ['user1@abakus.no', 'user2@abakus.no'])

    def test_generic_mappings_recipients_list_invalid_queryset(self):
        generic_model_test = GenericModelTest(empty_queryset=None)
        generic_model_test.save()
        generic_mapping = GenericMapping(content_object=generic_model_test)
        generic_mapping.save()
        self.assertEqual(generic_mapping.get_recipients(), [])

    def test_generic_mappings_recipients_list_empty_queryset(self):
        generic_model_test = GenericModelTest(empty_queryset=True)
        generic_model_test.save()
        generic_mapping = GenericMapping(content_object=generic_model_test)
        generic_mapping.save()
        self.assertEqual(generic_mapping.get_recipients(), [])

    def test_generic_mapping_mixin(self):
        try:
            mixin = GenericMappingMixin()
            mixin.get_mail_recipients()
        except Exception as ex:
            self.assertEqual(isinstance(ex, NotImplementedError), True)
