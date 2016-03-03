from rest_framework import viewsets

from lego.app.comments.models import Comment
from lego.app.comments.permissions import CommentPermissions
from lego.app.comments.serializers import CommentSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (CommentPermissions,)
