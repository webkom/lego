from basis.serializers import BasisSerializer
from rest_framework import serializers
from rest_framework.fields import CharField

from lego.app.comments.serializers import CommentSerializer
from lego.app.events.models import Event, Pool, Registration


class PoolSerializer(BasisSerializer):
    class Meta:
        model = Pool
        fields = ('id', 'name', 'capacity', 'event', 'activation_date', 'permission_groups')


class EventCreateAndUpdateSerializer(BasisSerializer):
    class Meta:
        model = Event
        fields = ('id', 'title', 'author', 'description', 'text', 'event_type', 'location',
                  'start_time', 'end_time', 'merge_time')


class EventReadSerializer(BasisSerializer):
    comments = CommentSerializer(read_only=True, many=True)
    comment_target = CharField(read_only=True)
    pools = PoolSerializer(many=True)
    capacity = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = ('id', 'title', 'author', 'description', 'text', 'event_type', 'location',
                  'comments', 'comment_target', 'start_time', 'end_time', 'pools',
                  'capacity', 'waiting_list')


class RegistrationCreateAndUpdateSerializer(BasisSerializer):
    class Meta:
        model = Registration
        fields = ('id', 'user', 'event', 'pool')
