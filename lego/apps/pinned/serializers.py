from django.utils import timezone
from rest_framework import serializers

from lego.apps.articles.serializers import PublicArticleSerializer
from lego.apps.events.serializers.events import EventSearchSerializer
from lego.apps.pinned.models import Pinned
from lego.apps.users.models import AbakusGroup
from lego.apps.users.serializers.abakus_groups import PublicAbakusGroupSerializer
from lego.apps.users.serializers.users import PublicUserSerializer
from lego.utils.fields import PrimaryKeyRelatedFieldNoPKOpt
from lego.utils.serializers import BasisModelSerializer


class ListPinnedSerializer(BasisModelSerializer):
    author = PublicUserSerializer(read_only=True, source='created_by')

    event = EventSearchSerializer()
    article = PublicArticleSerializer()

    target_groups = PublicAbakusGroupSerializer(many=True)

    content_type = serializers.SerializerMethodField()
    pinned_now = serializers.SerializerMethodField()

    def get_content_type(self, obj):
        return 'event' if obj.event is not None else 'article'

    def get_pinned_now(self, obj):
        return obj.pinned_from <= timezone.now().date() and obj.pinned_to >= timezone.now().date()

    class Meta:
        model = Pinned
        fields = (
            'id', 'created_at', 'author', 'article', 'event', 'target_groups', 'pinned_from',
            'pinned_to', 'content_type', 'pinned_now'
        )


class FrontpagePinnedSerializer(BasisModelSerializer):
    event = EventSearchSerializer()
    article = PublicArticleSerializer()

    content_type = serializers.SerializerMethodField()
    pinned_now = serializers.SerializerMethodField()

    def get_content_type(self, obj):
        return 'event' if obj.event is not None else 'article'

    def get_pinned_now(self, obj):
        return True

    class Meta:
        model = Pinned
        fields = (
            'id', 'created_at', 'article', 'event', 'pinned_from', 'pinned_to', 'content_type',
            'pinned_now'
        )


class CreatePinnedSerializer(BasisModelSerializer):
    target_groups = PrimaryKeyRelatedFieldNoPKOpt(many=True, queryset=AbakusGroup.objects.all())

    def validate(self, data):
        if 'event' not in data and 'article' not in data:
            raise serializers.ValidationError('either event or article must be defined')
        if data.get('event') and data.get('article'):
            raise serializers.ValidationError('both event and article cant be defined')
        return data

    class Meta:
        model = Pinned
        fields = ('article', 'event', 'target_groups', 'pinned_from', 'pinned_to')
