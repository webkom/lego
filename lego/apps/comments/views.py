from rest_framework import mixins, viewsets

from lego.apps.comments.models import Comment
from lego.apps.comments.serializers import CommentSerializer, UpdateCommentSerializer
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

    def perform_create(self, serializer):
        self._check_content_object_lock(serializer)
        super().perform_create(serializer)

    def perform_update(self, serializer):
        self._check_content_object_lock(serializer)
        super().perform_update(serializer)

    def _check_content_object_lock(self, serializer):
        content_type_id = serializer.validated_data.get("content_type").id
        object_id = serializer.validated_data.get("object_id")
        content_type = ContentType.objects.get_for_id(content_type_id)

        # Adapt this part to your model's specifics
        if content_type.model == "thread" and content_type.app_label == "forums":
            ThreadModel = content_type.model_class()
            thread = ThreadModel.objects.get(id=object_id)
            if thread.is_locked:  # Assume `is_locked` is a property/method to check lock status
                raise PermissionDenied("This thread is locked.")