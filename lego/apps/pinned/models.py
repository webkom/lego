from django.db import models

from lego.apps.articles.models import Article
from lego.apps.events.models import Event
from lego.apps.users.models import AbakusGroup
from lego.utils.models import BasisModel

# Create your models here.


class PinnedEvent(BasisModel):
    pinned_from = models.DateField()
    pinned_to = models.DateField()

    event = models.ForeignKey(
        Event, related_name='group_pins', on_delete=models.SET_NULL, null=True
    )
    target_groups = models.ManyToManyField(AbakusGroup)


class PinnedArticle(BasisModel):
    pinned_from = models.DateField()
    pinned_to = models.DateField()

    article = models.ForeignKey(
        Article, related_name='group_pins', on_delete=models.SET_NULL, null=True
    )
    target_groups = models.ManyToManyField(AbakusGroup)
