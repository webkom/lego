from rest_framework import serializers


class SlackInviteSerializer(serializers.Serializer):
    email = serializers.EmailField()
