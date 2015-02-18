from basis.serializers import BasisSerializer
from rest_framework.fields import CharField

from lego.app.comments.serializers import CommentSerializer
from lego.app.events.models import Event, Pool


class PoolSerializer(BasisSerializer):

    class Meta:
        model = Pool


class EventSerializer(BasisSerializer):
    comments = CommentSerializer(read_only=True, many=True)
    comment_target = CharField(read_only=True)
    pools = PoolSerializer(many=True, required=False)

    class Meta:
        model = Event
        fields = ('id', 'title', 'description', 'text', 'comments', 'comment_target', 'end_time',
                  'event_type', 'location', 'author', 'start_time')

    def create(self, validated_data):
        print(validated_data)
        pool_data = validated_data.pop('pools')
        event = Event.objects.create(**validated_data)
        Pool.objects.create(event=event, **pool_data)
        return event
