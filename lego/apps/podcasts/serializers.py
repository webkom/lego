from lego.apps.content.fields import ContentSerializerField
from lego.apps.podcasts.models import Podcast
from lego.apps.users.fields import PublicUserField
from lego.apps.users.models import User
from lego.apps.users.serializers.users import PublicUserSerializer
from lego.utils.serializers import BasisModelSerializer


class PodcastSerializer(BasisModelSerializer):

    description = ContentSerializerField()
    authors = PublicUserSerializer(many=True)
    thanks = PublicUserSerializer(many=True)

    class Meta:
        model = Podcast
        fields = ('id', 'source', 'created_at', 'description', 'authors', 'thanks')


class DetailedPodcastSerializer(BasisModelSerializer):

    description = ContentSerializerField()
    authors = PublicUserSerializer(many=True)
    thanks = PublicUserSerializer(many=True)

    class Meta:
        model = Podcast
        fields = ('id', 'source', 'created_at', 'description', 'authors', 'thanks')


class PodcastCreateAndUpdateSerializer(BasisModelSerializer):

    description = ContentSerializerField()
    authors = PublicUserField(many=True, queryset=User.objects.all())
    thanks = PublicUserField(many=True, queryset=User.objects.all())

    class Meta:
        model = Podcast
        fields = ('id', 'source', 'description', 'authors', 'thanks')
