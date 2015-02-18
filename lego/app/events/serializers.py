from basis.serializers import BasisSerializer

from lego.app.events.models import Event, Pool


class PoolSerializer(BasisSerializer):

    class Meta:
        model = Pool
        fields = ('name', 'size', 'activation_date')


class EventSerializer(BasisSerializer):

    pools = PoolSerializer(many=True, required=False)

    class Meta:
        model = Event

    def create(self, validated_data):
        pool_data = validated_data.pop('pools')
        event = Event.objects.create(**validated_data)
        for pool in pool_data:
            Pool.objects.create(event=event, **pool)
        return event
