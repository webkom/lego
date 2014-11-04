# -*- coding: utf8 -*-
from django.contrib.contenttypes.models import ContentType


class MappingResult(object):
    def get_recipients(self):
        raise NotImplemented('Please implement the get_recipients method.')


class GenericMappingMixin(object):
    def get_mail_recipients(self):
        """
        :return: user queryset
        """
        raise NotImplementedError('Please implement the get_mail_recipients method.')

    def get_generic_mapping(self):
        from.models import GenericMapping
        obj, created = GenericMapping.objects.get_or_create(
            content_id=self.id,
            content_type=ContentType.objects.get_for_model(self)
        )
        return obj
