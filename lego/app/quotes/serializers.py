from basis.serializers import BasisSerializer
from rest_framework import serializers

from lego.app.quotes.models import Quote, QuoteLike
from lego.app.quotes.permissions import QuotePermissions
from lego.users.serializers import PublicUserSerializer


class QuoteSerializer(BasisSerializer):
    has_liked = serializers.SerializerMethodField('user_has_liked')
    author = serializers.SerializerMethodField('user_author')
    permissions = serializers.SerializerMethodField('user_permissions')

    def user_permissions(self, obj):
        user = self.context['request'].user
        permissions = []
        if user.has_perm(QuotePermissions.perms_map['approve']):
            permissions.append('can_approve')
        return permissions

    def user_has_liked(self, obj):
        return obj.has_liked(user=self.context['request'].user)

    def user_author(self, obj):
        user = self.context['request'].user
        if user.has_perm(QuotePermissions.perms_map['approve']):
            return PublicUserSerializer(obj.author).data
        else:
            return None

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
        return Quote.objects.create(**validated_data)


class QuoteLikeSerializer(BasisSerializer):
    class Meta:
        model = QuoteLike
        fields = ('user', 'quote')
