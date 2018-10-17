from rest_framework import permissions, viewsets


from lego.apps.podcasts.models import Podcast
from lego.apps.podcasts.serializers import \
    PodcastCreateAndUpdateSerializer, \
    PodcastSerializer, \
    DetailedPodcastSerializer
from lego.apps.permissions.api.views import AllowedPermissionsMixin


class PodcastViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):

    ordering = 'created_at'

    queryset = Podcast.objects.all()

    def get_serializer_class(self):
        print(self.action)
        if self.action in ['create', 'update', 'partial_update']:
            return PodcastCreateAndUpdateSerializer
        elif self.action == 'retrieve':
            return DetailedPodcastSerializer
        return PodcastSerializer

