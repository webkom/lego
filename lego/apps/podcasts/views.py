from rest_framework import permissions, viewsets


from lego.apps.podcasts.models import Podcast
from lego.apps.podcasts.serializers import \
    PodcastCreateAndUpdateSerializer, \
    PodcastSerializer, \
    DetailedPodcastSerializer


class PodcastViewSet(viewsets.ModelViewSet):

    ordering = 'created_at'

    permission_classes = (permissions.AllowAny,)

    queryset = Podcast.objects.all()

    def get_serializer_class(self):
        print(self.action)
        if self.action in ['create', 'update', 'partial_update']:
            return PodcastCreateAndUpdateSerializer
        elif self.action == 'retrieve':
            return DetailedPodcastSerializer
        return PodcastSerializer

