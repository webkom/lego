from lego.apps.articles.models import Article
from lego.apps.articles.serializers import PublicArticleSerializer
from lego.apps.events.models import Event
from lego.apps.events.serializers.events import EventSearchSerializer
from lego.apps.pinned.models import PinnedArticle, PinnedEvent
from lego.apps.users.models import AbakusGroup
from lego.apps.users.serializers.abakus_groups import PublicAbakusGroupSerializer
from lego.apps.users.serializers.users import PublicUserSerializer
from lego.utils.fields import PrimaryKeyRelatedFieldNoPKOpt
from lego.utils.serializers import BasisModelSerializer


class PinnedEventSerializer(BasisModelSerializer):
    author = PublicUserSerializer(read_only=True, source='created_by')

    event = EventSearchSerializer()
    target_groups = PublicAbakusGroupSerializer(many=True)

    class Meta:
        model = PinnedEvent
        fields = ('id', 'created_at', 'author', 'event', 'target_groups')


class CreatePinnedEventSerializer(BasisModelSerializer):
    author = PublicUserSerializer(read_only=True, source='created_by')

    event = PrimaryKeyRelatedFieldNoPKOpt(queryset=Event.objects.all())
    target_groups = PrimaryKeyRelatedFieldNoPKOpt(many=True, queryset=AbakusGroup.objects.all())

    class Meta:
        model = PinnedEvent
        fields = ('id', 'created_at', 'author', 'event', 'target_groups')


class PinnedArticleSerializer(BasisModelSerializer):
    author = PublicUserSerializer(read_only=True, source='created_by')

    article = PublicArticleSerializer()

    target_groups = PublicAbakusGroupSerializer(many=True)

    class Meta:
        model = PinnedArticle
        fields = ('id', 'created_at', 'author', 'article', 'target_groups')


class CreatePinnedArticleSerializer(BasisModelSerializer):
    author = PublicUserSerializer(read_only=True, source='created_by')

    article = PrimaryKeyRelatedFieldNoPKOpt(queryset=Article.objects.all())
    target_groups = PrimaryKeyRelatedFieldNoPKOpt(many=True, queryset=AbakusGroup.objects.all())

    class Meta:
        model = PinnedArticle
        fields = ('id', 'created_at', 'author', 'article', 'target_groups')
