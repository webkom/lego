from django.db.models import CASCADE, ForeignKey
from django.db import models

from lego.apps.content.models import Content
from lego.apps.forums.permissions import ForumPermissionHandler, ThreadPermissionHandler
from lego.apps.permissions.models import ObjectPermissionsModel
from lego.utils.models import BasisModel


class Forum(Content, BasisModel, ObjectPermissionsModel):
    sticky = models.PositiveIntegerField(null=False, blank=False, default=0)
    class Meta:
        abstract = False
        permission_handler = ForumPermissionHandler()


class Thread(Content, BasisModel, ObjectPermissionsModel):
    forum = ForeignKey(Forum, on_delete=CASCADE, related_name="threads")
    sticky = models.PositiveIntegerField(null=False, blank=False, default=0)
    locked = models.BooleanField(default=False, null=False, blank=False)
    class Meta:
        abstract = False
        permission_handler = ThreadPermissionHandler()
