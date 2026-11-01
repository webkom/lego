from rest_framework import serializers

from drf_spectacular.utils import extend_schema_serializer

from lego.apps.articles.serializers import PublicArticleSerializer
from lego.apps.events.serializers.events import FrontpageEventSerializer
from lego.apps.polls.serializers import DetailedPollSerializer


@extend_schema_serializer(many=False)
class FrontpageSerializer(serializers.Serializer):
    articles = PublicArticleSerializer(many=True)
    events = FrontpageEventSerializer(many=True)
    poll = DetailedPollSerializer(allow_null=True)
