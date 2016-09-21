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

    def get_like(self, user):
        content_type = ContentType.objects.get_for_model(self)
        return Like.objects.filter(content_type=content_type, object_id=self.id, user=user)

    def get_likes(self):
        content_type = ContentType.objects.get_for_model(self)
        return Like.objects.filter(content_type=content_type, object_id=self.id)

    def has_liked(self, user):
        content_type = ContentType.objects.get_for_model(self)
        return Like.objects.filter(content_type=content_type, object_id=self.id, user=user).exists()

    def like(self, user):
        Like.objects.create(user=user, content_object=self)

    def unlike(self, user):
        content_type = ContentType.objects.get_for_model(self)
        Like.objects.filter(content_type=content_type, object_id=self.id, user=user).delete()
