from rest_framework import serializers
from rest_framework.fields import CharField

from lego.apps.comments.serializers.comments import CommentSerializer
from lego.apps.content.fields import ContentSerializerField
from lego.apps.forums.models import Forum, Thread
from lego.apps.users.serializers.users import PublicUserSerializer
from lego.utils.serializers import (
    BasisModelSerializer,
    ObjectPermissionsSerializerMixin,
)


class DetailedThreadSerializer(BasisModelSerializer):
    forum = serializers.PrimaryKeyRelatedField(queryset=Forum.objects.all())
    comments = CommentSerializer(read_only=True, many=True)
    created_by = PublicUserSerializer(read_only=True)
    content_target = CharField(read_only=True)
    content = ContentSerializerField(source="text", required=True)

    class Meta:
        model = Thread
        fields = (
            "id",
            "title",
            "content",
            "comments",
            "created_at",
            "forum",
            "created_by",
            "content_target",
        )


class DetailedAdminThreadSerializer(
    ObjectPermissionsSerializerMixin, DetailedThreadSerializer
):
    class Meta:
        model = Thread
        fields = (
            DetailedThreadSerializer.Meta.fields
            + ObjectPermissionsSerializerMixin.Meta.fields
        )


class PublicThreadSerializer(BasisModelSerializer):
    forum = serializers.PrimaryKeyRelatedField(queryset=Forum.objects.all())
    content = ContentSerializerField(source="text")

    class Meta:
        model = Thread
        fields = ("id", "title", "content", "created_at", "forum")


class DetailedForumSerializer(BasisModelSerializer):
    threads = PublicThreadSerializer(many=True, read_only=True)
    created_by = PublicUserSerializer(read_only=True)
    content_target = CharField(read_only=True)

    class Meta:
        model = Forum
        fields = (
            "id",
            "title",
            "description",
            "created_at",
            "threads",
            "created_by",
            "content_target",
        )


class DetailedAdminForumSerializer(
    ObjectPermissionsSerializerMixin, DetailedForumSerializer
):
    class Meta:
        model = Forum
        fields = (
            DetailedForumSerializer.Meta.fields
            + ObjectPermissionsSerializerMixin.Meta.fields
        )


class PublicForumSerializer(BasisModelSerializer):
    class Meta:
        model = Forum
        fields = (
            "id",
            "title",
            "description",
            "created_at",
        )
