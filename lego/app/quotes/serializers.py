from basis.serializers import BasisSerializer

from lego.app.quotes.models import Quote, QuoteLike
from lego.app.quotes.permissions import QuotePermissions
from lego.users.models import User
from rest_framework import serializers


class QuoteSerializer(BasisSerializer):
    class Meta:
        model = Quote


class QuoteReadSerializer(BasisSerializer):
    has_liked = serializers.SerializerMethodField('user_has_liked')
    permissions = serializers.SerializerMethodField('user_permissions')

    class Meta:
        model = Quote
        fields = ('id', 'title', 'author', 'quote', 'source', 'approved', 'likes', 'has_liked', 'permissions')

    def user_has_liked(self, obj):
        return obj.has_liked(user=self.context['request'].user)

    def user_permissions(self, obj):
        user = self.context['request'].user
        permissions = []
        if user.has_perm(QuotePermissions.perms_map['approve']):
            permissions.append('can_approve')
        return permissions

    def create(self, validated_data):
        return Quote.objects.create(**validated_data)

class QuoteCreateAndUpdateSerializer(BasisSerializer):
    class Meta:
        model = Quote
        fields = ('id', 'title', 'author', 'quote', 'source', 'approved', 'likes')

    def create(self, validated_data):
        return Quote.objects.create(**validated_data)


class QuoteLikeSerializer(BasisSerializer):
    class Meta:
        model = QuoteLike
        fields = ('user', 'quote')
