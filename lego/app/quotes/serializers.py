from basis.serializers import BasisSerializer

from lego.app.quotes.models import Quote, QuoteLike
from lego.app.quotes.permissions import QuotePermissions
from lego.users.models import User
from rest_framework import serializers

class DynamicFieldsModelSerializer(BasisSerializer):

    def __init__(self, *args, **kwargs):
        remove_fields = kwargs.pop('remove_fields', None)

        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if remove_fields is not None:
            for field_name in remove_fields:
                self.fields.pop(field_name)

class QuoteSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Quote

class QuoteReadSerializer(DynamicFieldsModelSerializer):
    has_liked = serializers.SerializerMethodField('user_has_liked')
    permissions = serializers.SerializerMethodField('user_permissions')
    author = serializers.SerializerMethodField('user_author')

    class Meta:
        model = Quote
        fields = ('id', 'title', 'author', 'quote', 'source', 'approved', 'likes', 'has_liked', 'permissions')

    def user_author(self, obj):
        return {
            'id': obj.author.pk,
            'username': obj.author.username
        }

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

class QuoteCreateAndUpdateSerializer(DynamicFieldsModelSerializer):
    permissions = serializers.SerializerMethodField('user_permissions')
    author = serializers.SerializerMethodField('user_author')

    class Meta:
        model = Quote
        fields = ('id', 'title', 'author', 'quote', 'source', 'approved', 'likes', 'permissions')

    def user_author(self, obj):
        return {
            'id': obj.author.pk,
            'username': obj.author.username
        }

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
