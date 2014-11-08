# -*- coding: utf8 -*-
import uuid
from datetime import timedelta
import collections

from basis.models import TimeStampModel

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import validate_email, ValidationError
from django.utils import timezone

from lego.users.models import User, AbakusGroup as Group
from .mixins import MappingResult


class MailMapping(TimeStampModel):
    address = models.CharField(max_length=100, verbose_name=_('Addess'), unique=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        try:
            validate_email('%s@abakus.no' % self.address)
        except ValidationError:
            raise ValidationError('Invalid local part.')

        self.address = self.address.lower()

        super(MailMapping, self).save(*args, **kwargs)


class UserMapping(MailMapping, MappingResult):
    user = models.ForeignKey(User, verbose_name=_('User'), related_name='mail_mappings')

    def __str__(self):
        return '%s@%s -> %s' % (self.address, settings.MAIL_MASTER_DOMAIN,
                                self.user.get_full_name())

    def get_recipients(self):
        if self.user.email:
            return [self.user.email]


class GroupMapping(MailMapping, MappingResult):
    group = models.ForeignKey(Group, verbose_name=_('Group'), related_name='mail_mappings')
    additional_users = models.ManyToManyField(User, verbose_name=_('Additional Users'), blank=True)

    def __str__(self):
        return '%s@%s -> %s' % (self.address, settings.MAIL_MASTER_DOMAIN, self.group.name)

    def get_recipients(self):
        recipients_list = []

        def get_mail(user):
            if user.email:
                return user.email

        recipients_list += map(get_mail, self.group.users.all())
        recipients_list += map(get_mail, self.additional_users.all())

        return set(recipients_list)


class GenericMapping(models.Model, MappingResult):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def get_recipients(self):
        """
        Get a list of recipients addresses from a generic object
        """
        generic_object = self.content_object
        get_mail_recipients = getattr(generic_object, 'get_mail_recipients', None)
        if callable(get_mail_recipients):
            users = get_mail_recipients()
            recipent_list = []
            if isinstance(users, collections.Iterable):
                for user in users:
                    if isinstance(user, User):
                        recipent_list.append(user.email)
                return set(recipent_list)
        return []


class OneTimeMapping(TimeStampModel, MappingResult):
    token = models.CharField(max_length=36, verbose_name=_('Token'), default=str(uuid.uuid4()),
                             unique=True)
    from_address = models.EmailField(verbose_name=_('From Address'))
    timeout = models.DateTimeField(verbose_name=_('Timeout'),
                                   default=timezone.now() + timedelta(minutes=15))
    group_mappings = models.ManyToManyField(GroupMapping, verbose_name=_('Groups'),
                                            related_name='one_time_mappings')
    generic_mappings = models.ManyToManyField(GenericMapping, verbose_name=_('Generic Mappings'),
                                              related_name='one_time_mappings')

    def get_recipients(self):
        recipients = []

        def get_gueryset_mappings(queryset):
            recipients = []
            for mapping_object in queryset:
                recipients += mapping_object.get_recipients()
            return recipients

        recipients += get_gueryset_mappings(self.group_mappings.all())
        recipients += get_gueryset_mappings(self.generic_mappings.all())

        return set(recipients)

    def add_generic_mapping(self, object):
        self.generic_mappings.add(object.get_generic_mapping())

    @property
    def is_valid(self):
        return self.timeout > timezone.now()
