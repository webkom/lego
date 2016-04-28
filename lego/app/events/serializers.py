from basis.serializers import BasisSerializer
from rest_framework import serializers
from rest_framework.fields import CharField

from lego.app.comments.serializers import CommentSerializer
from lego.app.events.models import Event, Pool, Registration
from lego.users.serializers import PublicUserSerializer


class RegistrationReadSerializer(BasisSerializer):
    user = PublicUserSerializer()

    class Meta:
        model = Registration
        fields = ('id', 'user')


class PoolReadSerializer(BasisSerializer):
    registrations = RegistrationReadSerializer(many=True)

    class Meta:
        model = Pool
        fields = ('id', 'name', 'capacity', 'activation_date', 'permission_groups', 'registrations')

    def create(self, validated_data):
        event = Event.objects.get(pk=self.context['view'].kwargs['event_pk'])
        permission_groups = validated_data.pop('permission_groups')
        pool = Pool.objects.create(event=event, **validated_data)
        pool.permission_groups.set(permission_groups)
        return pool


class EventReadSerializer(BasisSerializer):
    comments = CommentSerializer(read_only=True, many=True)
    comment_target = CharField(read_only=True)

    class Meta:
        model = Event
        fields = ('id', 'title', 'author', 'description', 'text', 'event_type', 'location',
                  'comments', 'comment_target', 'start_time', 'end_time')


class EventReadDetailedSerializer(BasisSerializer):
    comments = CommentSerializer(read_only=True, many=True)
    comment_target = CharField(read_only=True)
    pools = PoolReadSerializer(many=True)
    capacity = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = ('id', 'title', 'author', 'description', 'text', 'event_type', 'location',
                  'comments', 'comment_target', 'start_time', 'end_time', 'pools', 'capacity')


class PoolCreateAndUpdateSerializer(BasisSerializer):

    class Meta:
        model = Pool
        fields = ('id', 'name', 'capacity', 'activation_date', 'permission_groups')

    def create(self, validated_data):
        event = Event.objects.get(pk=self.context['view'].kwargs['event_pk'])
        permission_groups = validated_data.pop('permission_groups')
        pool = Pool.objects.create(event=event, **validated_data)
        pool.permission_groups.set(permission_groups)

        return pool


class EventCreateAndUpdateSerializer(BasisSerializer):
    class Meta:
        model = Event
        fields = ('id', 'title', 'author', 'description', 'text', 'event_type', 'location',
                  'start_time', 'end_time', 'merge_time')


class RegistrationCreateAndUpdateSerializer(BasisSerializer):
    class Meta:
        model = Registration
        fields = ('id',)

    def create(self, validated_data):
        user = validated_data['current_user']
        event = Event.objects.get(pk=self.context['view'].kwargs['event_pk'])
        return event.register(user)
