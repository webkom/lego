from rest_framework import mixins, viewsets

from lego.apps.comments.models import Comment
from lego.apps.comments.serializers.comments import CommentSerializer, UpdateCommentSerializer
from lego.apps.permissions.api.views import AllowedPermissionsMixin


class CommentViewSet(
    AllowedPermissionsMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    NB: Don't add the ListMixin, this breaks permissions because the permissions
    handles requires an object.
    """

    queryset = Comment.objects.all()
    ordering = "created_at"

    def get_serializer_class(self):
        if self.action in ("update", "partial_update"):
            return UpdateCommentSerializer

        return CommentSerializer
