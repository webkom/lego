from django.db import models

from lego.apps.articles.models import Article
from lego.apps.events.models import Event
from lego.apps.users.models import AbakusGroup
from lego.utils.models import BasisModel


class Pinned(BasisModel):
    pinned_from = models.DateField()
    pinned_to = models.DateField()

    event = models.ForeignKey(
        Event, related_name='pins', on_delete=models.CASCADE, null=True, blank=True
    )
    article = models.ForeignKey(
        Article, related_name='pins', on_delete=models.CASCADE, null=True, blank=True
    )
    target_groups = models.ManyToManyField(AbakusGroup)
