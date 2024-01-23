from django.db.models import CASCADE, ForeignKey

from lego.apps.content.models import Content
from lego.apps.forums.permissions import ForumPermissionHandler, ThreadPermissionHandler
from lego.apps.permissions.models import ObjectPermissionsModel
from lego.utils.models import BasisModel


class Forum(Content, BasisModel, ObjectPermissionsModel):
    class Meta:
        abstract = False
        permission_handler = ForumPermissionHandler()


class Thread(Content, BasisModel, ObjectPermissionsModel):
    forum = ForeignKey(Forum, on_delete=CASCADE, related_name="threads")

    class Meta:
        abstract = False
        permission_handler = ThreadPermissionHandler()
