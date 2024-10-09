from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField, DateTimeField

from lego.apps.comments.models import Comment
from lego.apps.content.fields import ContentSerializerField
from lego.apps.users.serializers.users import PublicUserSerializer
from lego.utils.serializers import BasisModelSerializer, GenericRelationField


class CommentSerializer(BasisModelSerializer):
    author = PublicUserSerializer(read_only=True, source="created_by")
    created_at = DateTimeField(read_only=True)
    updated_at = DateTimeField(read_only=True)
    content_target = GenericRelationField(source="content_object")
    text = ContentSerializerField()
    reactions_grouped = serializers.SerializerMethodField()
    content_target_self = CharField(read_only=True)

    class Meta:
        model = Comment
        fields = (
            "id",
            "text",
            "author",
            "content_target",
            "content_target_self",
            "created_at",
            "updated_at",
            "parent",
            "reactions_grouped",
        )

    def get_reactions_grouped(self, obj):
        user = None
        if "request" in self.context:
            user = self.context["request"].user
        return obj.get_reactions_grouped(user)

    def validate(self, attrs):
        content_target = attrs.get("content_object")

        if content_target and "parent" in attrs:
            parent = attrs["parent"]
            if (
                parent.object_id != content_target.id
                or parent.content_type
                != ContentType.objects.get_for_model(content_target)
            ):
                raise ValidationError(
                    {"parent": "parent does not point to the same content_target"}
                )

        return attrs


class UpdateCommentSerializer(BasisModelSerializer):
    text = ContentSerializerField()

    class Meta:
        model = Comment
        fields = ("text",)
