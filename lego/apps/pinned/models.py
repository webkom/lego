from django.db import models

from lego.apps.articles.models import Article
from lego.apps.events.models import Event
from lego.apps.users.models import AbakusGroup
from lego.utils.models import BasisModel

# Create your models here.


class PinnedEvent(BasisModel):
    event = models.ForeignKey(
        Event, related_name='group_pins', on_delete=models.SET_NULL, null=True
    )
    target_groups = models.ManyToManyField(AbakusGroup)


class PinnedArticle(BasisModel):
    article = models.ForeignKey(
        Article, related_name='group_pins', on_delete=models.SET_NULL, null=True
    )
    target_groups = models.ManyToManyField(AbakusGroup)
