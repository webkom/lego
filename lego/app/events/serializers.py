from basis.serializers import BasisSerializer
from rest_framework import serializers
from rest_framework.fields import CharField

from lego.app.comments.serializers import CommentSerializer
from lego.app.events.models import Event, Pool


class PoolSerializer(BasisSerializer):

    class Meta:
        model = Pool
        fields = ('name', 'size', 'activation_date')


class EventSerializer(BasisSerializer):
    comments = CommentSerializer(read_only=True, many=True)
    comment_target = CharField(read_only=True)
    pools = PoolSerializer(many=True, required=False)
    total_capacity_count = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = ('id', 'title', 'author', 'description', 'text', 'event_type',
                  'location', 'comments', 'comment_target', 'start_time',
                  'end_time', 'merge_time', 'pools', 'total_capacity_count')

    def create(self, validated_data):
        pool_data = validated_data.pop('pools')
        event = Event.objects.create(**validated_data)
        for pool in pool_data:
            Pool.objects.create(event=event, **pool)
        return event
