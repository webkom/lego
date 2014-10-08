from datetime import datetime, timedelta

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from basis.models import BasisModel
from django.contrib.auth.models import User, Group  #TODO: Change this to custom user and group classes.


class MailMapping(BasisModel):
    address = models.CharField(max_length=100, verbose_name=_('Addess'), unique=True)

    class Meta:
        abstract = True


class UserMapping(MailMapping):
    user = models.ForeignKey(User, verbose_name=_('User'), related_name='mail_mappings')


class GroupMapping(MailMapping):
    group = models.ForeignKey(Group, verbose_name=_('Group'), related_name='mail_mappings')


class RawMapping(MailMapping):
    recipient = models.EmailField(verbose_name=_('Recipient'))
    description = models.TextField(verbose_name=_('Description'))



class GenericMappingMixin(models.Model):
    def get_mail_recipients(self):
        raise NotImplementedError()

    class Meta:
        abstract = True


class GenericMapping(MailMapping):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def get_recipients(self) -> (list):
        """
        Get a list of recipients addresses from a generic object
        """
        generic_object = self.content_object
        get_mail_recipients = getattr(generic_object, 'get_mail_recipients', None)
        if callable(get_mail_recipients):
            users = get_mail_recipients()
            recipent_list = []
            for user in users:
                if isinstance(user, User):
                    recipent_list.append(user.email)
            return recipent_list
        return []



class RestrictedMapping(MailMapping):
    user_mapping = models.ForeignKey(UserMapping, verbose_name=_('User Mapping'),
                                     related_name='restricted_mail_mappings', null=True)
    group_mapping = models.ForeignKey(GroupMapping, verbose_name=_('Group Mapping'),
                                      related_name='restricted_mail_mappings', null=True)
    generic_mapping = models.ForeignKey(GenericMapping, verbose_name=_('Generic Mapping'),
                                        related_name='restricted_mail_mappings', null=True)
    token = models.CharField(max_length=80, verbose_name=_('Token'))
    timeout = models.DateTimeField(verbose_name=_('Timeout'), default=datetime.now() + timedelta(minutes=15))
    sender = models.EmailField(verbose_name=_('Sender Mail'))