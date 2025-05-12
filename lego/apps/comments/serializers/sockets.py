from rest_framework import serializers

from lego.apps.comments.serializers.comments import CommentSerializer
from lego.apps.websockets.serializers import WebsocketSerializer


class CommentSocketSerializer(WebsocketSerializer):
    payload = CommentSerializer()
