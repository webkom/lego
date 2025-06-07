from rest_framework import serializers
from rest_framework.fields import CharField

from lego.apps.articles.models import Article
from lego.apps.comments.serializers.comments import CommentSerializer
from lego.apps.content.fields import ContentSerializerField
from lego.apps.files.fields import ImageField
from lego.apps.tags.serializers import TagSerializerMixin
from lego.apps.users.fields import PublicUserField
from lego.apps.users.models import User
from lego.apps.users.serializers.users import PublicUserSerializer
from lego.utils.serializers import (
    BasisModelSerializer,
    ObjectPermissionsSerializerMixin,
)


class DetailedArticleSerializer(TagSerializerMixin, BasisModelSerializer):
    comments = CommentSerializer(read_only=True, many=True)
    cover = ImageField(required=False, options={"height": 500})
    cover_placeholder = ImageField(
        source="cover", required=False, options={"height": 50, "filters": ["blur(20)"]}
    )
    content_target = CharField(read_only=True)
    content = ContentSerializerField(source="text")
    reactions_grouped = serializers.SerializerMethodField()
    authors = PublicUserField(
        queryset=User.objects.all(), allow_null=False, required=True, many=True
    )

    def get_reactions_grouped(self, obj):
        user = self.context["request"].user
        return obj.get_reactions_grouped(user)

    class Meta:
        model = Article
        fields = (
            "id",
            "title",
            "slug",
            "cover",
            "cover_placeholder",
            "authors",
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
    cover_placeholder = ImageField(
        source="cover", required=False, options={"height": 30, "filters": ["blur(20)"]}
    )
    authors = PublicUserSerializer(many=True)

    class Meta:
        model = Article
        fields = (
            "id",
            "title",
            "slug",
            "cover",
            "cover_placeholder",
            "authors",
            "description",
            "tags",
            "created_at",
            "pinned",
        )
