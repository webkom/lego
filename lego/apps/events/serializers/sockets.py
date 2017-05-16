from rest_framework import serializers


class MetaSerializer(serializers.Serializer):
    event_id = serializers.CharField(required=False)
    activation_time = serializers.DateTimeField(required=False)
    from_pool = serializers.IntegerField(required=False)
    error_msg = serializers.CharField(required=False)


class WebsocketSerializer(serializers.Serializer):
    type = serializers.CharField()
    meta = MetaSerializer()
    payload = serializers.DictField()
