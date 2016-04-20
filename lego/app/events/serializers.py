from basis.serializers import BasisSerializer
from rest_framework.fields import CharField

from lego.app.comments.serializers import CommentSerializer
from lego.app.events.models import Event


class EventSerializer(BasisSerializer):
    comments = CommentSerializer(read_only=True, many=True)
    comment_target = CharField(read_only=True)

    class Meta:
        model = Event
        fields = ('id', 'title', 'ingress', 'text', 'comments', 'comment_target', 'end_time',
                  'event_type', 'location', 'author', 'start_time')
