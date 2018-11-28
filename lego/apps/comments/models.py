from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from lego.apps.comments.permissions import CommentPermissionHandler
from lego.apps.content.fields import ContentField
from lego.utils.managers import BasisModelManager
from lego.utils.models import BasisModel


class CommentManager(BasisModelManager):
    def get_queryset(self):
        return super().get_queryset().select_related("created_by")


class Comment(BasisModel):

    text = ContentField(allow_images=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey()
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)

    objects = CommentManager()

    class Meta:
        ordering = ("created_at",)
        permission_handler = CommentPermissionHandler()

    def __str__(self):
        return self.text
