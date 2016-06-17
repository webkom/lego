from rest_framework import mixins, viewsets

from lego.app.comments.models import Comment
from lego.app.comments.serializers import CommentSerializer


class CommentViewSet(mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    queryset = Comment.objects.all().select_related('created_by')
    serializer_class = CommentSerializer
