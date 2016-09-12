from rest_framework import mixins, viewsets

from lego.apps.comments.models import Comment
from lego.apps.comments.permissions import CommentPermission
from lego.apps.comments.serializers import CommentSerializer


class CommentViewSet(mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    queryset = Comment.objects.all().select_related('created_by')
    serializer_class = CommentSerializer

    permission_classes = [CommentPermission]
