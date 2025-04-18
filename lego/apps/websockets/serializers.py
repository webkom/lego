from rest_framework import serializers


class WebsocketSerializer(serializers.Serializer):
    """
    Base serializer for WebSocket messages.

    Should be extended for specific message types implementing the payload and meta fields.
    """

    type = serializers.CharField()
    meta = serializers.DictField()
    payload = serializers.DictField()
