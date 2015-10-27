from basis.serializers import BasisSerializer

from lego.app.quotes.models import Quote, QuoteLike
from lego.app.quotes.permissions import QuotePermissions
from lego.users.models import User
from rest_framework import serializers

class QuoteSerializer(BasisSerializer):
    class Meta:
        model = Quote

class QuoteUnapprovedReadSerializer(BasisSerializer):
    has_liked = serializers.SerializerMethodField('user_has_liked')
    author = serializers.SerializerMethodField('user_author')

    class Meta:
        model = Quote
        fields = ('id', 'title', 'author', 'quote', 'source', 'approved', 'likes', 'has_liked')

    def user_author(self, obj):
        return {
            'id': obj.author.pk,
            'username': obj.author.username
        }

    def user_has_liked(self, obj):
        return obj.has_liked(user=self.context['request'].user)

    def create(self, validated_data):
        return Quote.objects.create(**validated_data)

class QuoteApprovedReadSerializer(BasisSerializer):
    has_liked = serializers.SerializerMethodField('user_has_liked')

    class Meta:
        model = Quote
        fields = ('id', 'title', 'quote', 'source', 'likes', 'has_liked')

    def user_has_liked(self, obj):
        return obj.has_liked(user=self.context['request'].user)

class QuoteCreateAndUpdateSerializer(BasisSerializer):
    permissions = serializers.SerializerMethodField('user_permissions')

    class Meta:
        model = Quote
        fields = ('id', 'title', 'author', 'quote', 'source', 'approved', 'likes', 'permissions')

    def user_permissions(self, obj):
        user = self.context['request'].user
        permissions = []
        if user.has_perm(QuotePermissions.perms_map['approve']):
            permissions.append('can_approve')
        return permissions

    def create(self, validated_data):
        return Quote.objects.create(**validated_data)


class QuoteLikeSerializer(BasisSerializer):
    class Meta:
        model = QuoteLike
        fields = ('user', 'quote')
