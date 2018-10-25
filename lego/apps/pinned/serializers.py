from rest_framework import serializers

from lego.apps.articles.serializers import PublicArticleSerializer
from lego.apps.events.serializers.events import EventSearchSerializer
from lego.apps.pinned.models import Pinned
from lego.apps.users.models import AbakusGroup
from lego.apps.users.serializers.abakus_groups import PublicAbakusGroupSerializer
from lego.apps.users.serializers.users import PublicUserSerializer
from lego.utils.fields import PrimaryKeyRelatedFieldNoPKOpt
from lego.utils.serializers import BasisModelSerializer


class PinnedEventSerializer(BasisModelSerializer):
    author = PublicUserSerializer(read_only=True, source='created_by')

    event = EventSearchSerializer()
    target_groups = PublicAbakusGroupSerializer(many=True)

    class Meta:
        model = Pinned
        fields = (
            'id', 'created_at', 'author', 'event', 'target_groups', 'pinned_from', 'pinned_to'
        )


class PinnedArticleSerializer(BasisModelSerializer):
    author = PublicUserSerializer(read_only=True, source='created_by')

    article = PublicArticleSerializer()

    target_groups = PublicAbakusGroupSerializer(many=True)

    class Meta:
        model = Pinned
        fields = (
            'id', 'created_at', 'author', 'article', 'target_groups', 'pinned_from', 'pinned_to'
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
