from django.contrib.contenttypes.models import ContentType
from lego.apps.likes.models import Like
from lego.apps.likes.serializers import LikeSerializer
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_409_CONFLICT


class LikeViewSet(viewsets.ModelViewSet):
    serializer_class = LikeSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post', 'head']

    def get_queryset(self):
        return Like.objects.all()

    def create(self, request, *args, **kwargs):
        content_type = get_object_or_404(ContentType, pk=request.data['content_type_id'])
        obj = get_object_or_404(content_type.model_class(), pk=request.data['object_id'])

        exists = Like.objects.filter(content_type=content_type, object_id=request.data['object_id'], user=request.user).exists()

        if exists:
            # Like already exists
            return Response(status=HTTP_409_CONFLICT)

        # Create the like
        like = Like.objects.create(user=request.user, content_object=obj)
        serializer = LikeSerializer(like, context={'request': request})
        return Response(
            serializer.data,
            status=HTTP_201_CREATED
        )

