from lego.utils.serializers import BasisModelSerializer
from lego.apps.podcasts.models import Podcast
from lego.apps.content.fields import ContentSerializerField
from lego.apps.users.serializers.users import PublicUserSerializer


class PodcastSerializer(BasisModelSerializer):

    description = ContentSerializerField()
    authors = PublicUserSerializer(many=True)

    class Meta:
        model = Podcast
        fields = (
            'id', 'source', 'created_at', 'title', 'description', 'authors'
        )


class DetailedPodcastSerializer(BasisModelSerializer):

    description = ContentSerializerField()
    authors = PublicUserSerializer(many=True)

    class Meta:
        model = Podcast
        fields = (
            'id', 'source', 'created_at', 'title', 'description', 'authors'
        )


class PodcastCreateAndUpdateSerializer(BasisModelSerializer):

    description = ContentSerializerField()

    class Meta:
        model = Podcast
        fields = (
            'source', 'created_at', 'title', 'description'
        )
