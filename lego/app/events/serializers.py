from rest_framework import serializers

from lego.app.events.models import Event


class EventSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Event
        fields = ('title', 'event_type', 'author', 'text', 'location', 'start_time', 'end_time')
