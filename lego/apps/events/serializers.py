from rest_framework import serializers
from rest_framework.fields import CharField

from lego.apps.comments.serializers import CommentSerializer
from lego.apps.events.models import Event, Pool, Registration
from lego.apps.users.serializers import PublicUserSerializer
from lego.utils.serializers import BasisModelSerializer


class RegistrationReadSerializer(BasisModelSerializer):
    user = PublicUserSerializer()

    class Meta:
        model = Registration
        fields = ('id', 'user')


class PoolReadSerializer(BasisModelSerializer):
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


class EventReadSerializer(BasisModelSerializer):
    comments = CommentSerializer(read_only=True, many=True)
    comment_target = CharField(read_only=True)

    class Meta:
        model = Event
        fields = ('id', 'title', 'author', 'description', 'text', 'event_type', 'location',
                  'comments', 'comment_target', 'start_time', 'end_time')


class EventReadDetailedSerializer(BasisModelSerializer):
    comments = CommentSerializer(read_only=True, many=True)
    comment_target = CharField(read_only=True)
    pools = PoolReadSerializer(many=True)
    capacity = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = ('id', 'title', 'author', 'description', 'text', 'event_type', 'location',
                  'comments', 'comment_target', 'start_time', 'end_time', 'pools', 'capacity')


class PoolCreateAndUpdateSerializer(BasisModelSerializer):

    class Meta:
        model = Pool
        fields = ('id', 'name', 'capacity', 'activation_date', 'permission_groups')

    def create(self, validated_data):
        event = Event.objects.get(pk=self.context['view'].kwargs['event_pk'])
        permission_groups = validated_data.pop('permission_groups')
        pool = Pool.objects.create(event=event, **validated_data)
        pool.permission_groups.set(permission_groups)

        return pool


class EventCreateAndUpdateSerializer(BasisModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'title', 'author', 'description', 'text', 'event_type', 'location',
                  'start_time', 'end_time', 'merge_time')


class RegistrationCreateAndUpdateSerializer(BasisModelSerializer):
    class Meta:
        model = Registration
        fields = ('id',)

    def create(self, validated_data):
        user = validated_data['current_user']
        event = Event.objects.get(pk=self.context['view'].kwargs['event_pk'])
        return event.register(user)
