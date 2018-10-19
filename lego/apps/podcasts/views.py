from rest_framework import viewsets

from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.podcasts.models import Podcast
from lego.apps.podcasts.serializers import (
    DetailedPodcastSerializer, PodcastCreateAndUpdateSerializer, PodcastSerializer
)


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
