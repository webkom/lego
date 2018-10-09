from lego.utils.serializers import BasisModelSerializer
from lego.apps.podcasts.models import Podcast
from lego.apps.content.fields import ContentSerializerField


class PodcastSerializer(BasisModelSerializer):

    class Meta:
        model = Podcast
        fields = (
            'id', 'created_at', 'title'
        )


class DetailedPodcastSerializer(BasisModelSerializer):

    description = ContentSerializerField()

    class Meta:
        model = Podcast
        fields = (
            'id', 'source', 'created_at', 'title', 'description'
        )


class PodcastCreateAndUpdateSerializer(BasisModelSerializer):

    description = ContentSerializerField()

    class Meta:
        model = Podcast
        fields = (
            'source', 'created_at', 'title', 'description'
        )
