from lego.apps.feeds.serializers.feeds import AggregatedFeedSerializer
from lego.apps.websockets.serializers import WebsocketSerializer


class FeedActivitySocketSerializer(WebsocketSerializer):
    payload = AggregatedFeedSerializer()
    meta = {}
