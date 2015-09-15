from basis.serializers import BasisSerializer
from rest_framework import serializers
from rest_framework.fields import CharField

from lego.app.comments.serializers import CommentSerializer
from lego.app.events.models import Event, Pool


class PoolSerializer(BasisSerializer):

    class Meta:
        model = Pool
        fields = ('name', 'capacity', 'activation_date', 'permission_groups')


class EventCreateAndUpdateSerializer(BasisSerializer):
    pools = PoolSerializer(many=True)
    capacity = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = ('id', 'title', 'author', 'description', 'text', 'event_type', 'location',
                  'start_time', 'end_time', 'merge_time', 'pools', 'capacity')

    def create(self, validated_data):
        pools_data = validated_data.pop('pools')
        event = Event.objects.create(**validated_data)
        for pool in pools_data:
            event.add_pool(**pool)
        return event


class EventReadSerializer(BasisSerializer):
    comments = CommentSerializer(read_only=True, many=True)
    comment_target = CharField(read_only=True)

    class Meta:
        model = Event
        fields = ('title', 'author', 'description', 'text', 'event_type', 'location',
                  'comments', 'comment_target', 'start_time', 'end_time', 'pools',
                  'capacity', 'waiting_list')
