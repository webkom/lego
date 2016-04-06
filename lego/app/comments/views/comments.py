from rest_framework import viewsets, mixins

from lego.app.comments.models import Comment
from lego.app.comments.permissions import CommentPermissions
from lego.app.comments.serializers import CommentSerializer


class CommentViewSet(mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (CommentPermissions,)
