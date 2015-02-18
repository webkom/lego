from rest_framework import serializers
from basis.serializers import BasisSerializer

from lego.app.events.models import Event, Pool


class PoolSerializer(BasisSerializer):

    class Meta:
        model = Pool
        fields = ('name', 'size', 'activation_date')


class EventSerializer(BasisSerializer):

    pools = PoolSerializer(many=True)
    total_capacity_count = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = ('title', 'author', 'ingress', 'text', 'event_type', 'location',
                  'start_time', 'end_time', 'merge_time', 'pools', 'total_capacity_count')

    def create(self, validated_data):
        pool_data = validated_data.pop('pools')
        event = Event.objects.create(**validated_data)
        for pool in pool_data:
            Pool.objects.create(event=event, **pool)
        return event
