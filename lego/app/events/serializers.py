from rest_framework import serializers

from lego.app.events.models import Event


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
