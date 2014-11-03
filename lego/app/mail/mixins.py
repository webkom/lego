# -*- coding: utf8 -*-


class MappingResult(object):
    def get_recipients(self):
        raise NotImplemented('Please implement the get_recipients method.')


class GenericMappingMixin(object):
    def get_mail_recipients(self):
        """
        :return: user queryset
        """
        raise NotImplementedError('Please implement the get_mail_recipients method.')
