from lego.apps.comments.serializers.comments import CommentSerializer
from lego.apps.websockets.serializers import WebsocketSerializer

from rest_framework import serializers


class CommentSocketSerializer(WebsocketSerializer):
    payload = CommentSerializer()
