from rest_framework import serializers

from lego.app.events.models import Event


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('title', 'event_type', 'author', 'ingress',
                  'text', 'location', 'start_time', 'end_time')
