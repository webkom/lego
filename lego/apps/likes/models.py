from basis.models import BasisModel
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from lego.apps.permissions.models import ObjectPermissionsModel

from lego.apps.users.models import User


class Like(BasisModel, ObjectPermissionsModel):
    user = models.ForeignKey(User, related_name='likes')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = (('user', 'content_type', 'object_id'),)


class Likeable(models.Model):
    likes = GenericRelation(Like,)

    class Meta:
        abstract = True

    def has_liked(self, user):
        return Like.objects.filter(user=user, content_object=self).exists()

    def like(self, user):
        Like.objects.create(user=user, content_object=self)

    def unlike(self, user):
        Like.objects.filter(user=user, content_object=self).delete()

