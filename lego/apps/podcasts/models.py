from django.db import models

from lego.apps.podcasts.permissions import PodcastPermissionHandler
from lego.utils.models import BasisModel


class Podcast(BasisModel):
    source = models.CharField(max_length=500)
    description = models.TextField()
    authors = models.ManyToManyField('users.User', related_name="authors", blank=True)
    thanks = models.ManyToManyField('users.User', related_name="thanks", blank=True)

    def _str_(self):
        return self.source

    class Meta:
        permission_handler = PodcastPermissionHandler()
