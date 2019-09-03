from rest_framework import serializers
from rest_framework.fields import CharField

from lego.apps.articles.models import Article
from lego.apps.comments.serializers import CommentSerializer
from lego.apps.content.fields import ContentSerializerField
from lego.apps.files.fields import ImageField
from lego.apps.tags.serializers import TagSerializerMixin
from lego.apps.users.serializers.users import PublicUserSerializer
from lego.utils.serializers import (
    BasisModelSerializer,
    ObjectPermissionsSerializerMixin,
)


class DetailedArticleSerializer(TagSerializerMixin, BasisModelSerializer):
    author = PublicUserSerializer(read_only=True, source="created_by")
    comments = CommentSerializer(read_only=True, many=True)
    cover = ImageField(required=False, options={"height": 500})
    content_target = CharField(read_only=True)
    content = ContentSerializerField(source="text")
    reactions_grouped = serializers.SerializerMethodField()

    def get_reactions_grouped(self, obj):
        user = self.context["request"].user
        return obj.get_reactions_grouped(user)

    class Meta:
        model = Article
        fields = (
            "id",
            "title",
            "cover",
            "author",
            "description",
            "comments",
            "content_target",
            "tags",
            "content",
            "created_at",
            "pinned",
            "reactions_grouped",
            "youtube_url",
        )


class DetailedArticleAdminSerializer(
    ObjectPermissionsSerializerMixin, DetailedArticleSerializer
):
    class Meta:
        model = Article
        fields = (
            DetailedArticleSerializer.Meta.fields
            + ObjectPermissionsSerializerMixin.Meta.fields
        )


class SearchArticleSerializer(BasisModelSerializer):
    cover = ImageField(required=False, options={"height": 500})
    content = ContentSerializerField(source="text")

    class Meta:
        model = Article
        fields = (
            "id",
            "title",
            "cover",
            "description",
            "content",
            "pinned",
            "created_at",
        )


class PublicArticleSerializer(TagSerializerMixin, BasisModelSerializer):

    cover = ImageField(required=False, options={"height": 300})
    author = PublicUserSerializer(read_only=True, source="created_by")

    class Meta:
        model = Article
        fields = (
            "id",
            "title",
            "cover",
            "author",
            "description",
            "tags",
            "created_at",
            "pinned",
        )
