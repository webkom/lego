from django.db import models

from lego.utils.models import BasisModel


class Podcast(BasisModel):
    source = models.CharField(max_length=300)
    title = models.CharField(max_length=300)
    description = models.TextField()

    class Meta:
        pass

    def _str_(self):
        return self.title
