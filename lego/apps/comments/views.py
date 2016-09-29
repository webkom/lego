from rest_framework import mixins, viewsets

from lego.apps.comments.models import Comment
from lego.apps.comments.permissions import CommentPermission
from lego.apps.comments.serializers import CommentSerializer, UpdateCommentSerializer


class CommentViewSet(mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    queryset = Comment.objects.all()
    permission_classes = (CommentPermission,)

    def get_serializer_class(self):
        if self.action in ('update', 'partial_update'):
            return UpdateCommentSerializer

        return CommentSerializer
