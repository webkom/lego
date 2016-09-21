from basis.serializers import BasisSerializer
from lego.apps.likes.models import Like
from lego.apps.quotes.models import Quote
from lego.apps.users.serializers import PublicUserSerializer
from rest_framework import serializers


class QuoteSerializer(BasisSerializer):
    has_liked = serializers.SerializerMethodField('user_has_liked')
    author = serializers.SerializerMethodField('user_author')
    permissions = serializers.SerializerMethodField('user_permissions')
    likes = serializers.SerializerMethodField('user_likes')

    def user_permissions(self, obj):
        user = self.context['request'].user
        permissions = []
        if user.has_perm('/sudo/admin/quotes/change-approval/'):
            permissions.append('can_approve')
        return permissions

    def user_has_liked(self, obj):
        return obj.has_liked(user=self.context['request'].user)

    def user_author(self, obj):
        user = self.context['request'].user
        if user.has_perm('/sudo/admin/quotes/change-approval/'):
            return PublicUserSerializer(obj.author).data
        else:
            return None

    def user_likes(self, obj):
        return obj.get_likes()

    class Meta:
        model = Quote
        fields = (
            'id',
            'created_at',
            'title',
            'author',
            'text',
            'source',
            'approved',
            'likes',
            'has_liked',
            'permissions'
        )

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return Quote.objects.create(**validated_data)


class QuoteLikeSerializer(BasisSerializer):
    class Meta:
        model = Like
        fields = ('user', 'quote')
