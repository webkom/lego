from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError, models
from rest_framework.exceptions import ValidationError

from lego.apps.emojis.models import Emoji
from lego.apps.reactions.constants import REACTION_COUNT_LIMIT
from lego.apps.reactions.exceptions import ReactionExists, TooManyReactions
from lego.apps.reactions.permissions import ReactionPermissionHandler
from lego.utils.managers import BasisModelManager
from lego.utils.models import BasisModel


class ReactionManager(BasisModelManager):
    def get_queryset(self):
        return super().get_queryset().select_related("created_by")


class Reaction(BasisModel):
    emoji = models.ForeignKey(Emoji, on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey()

    objects = ReactionManager()

    class Meta:
        permission_handler = ReactionPermissionHandler()

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"{self.created_by} - {self.emoji.pk}"

    def save(self, *args, **kwargs):
        if Reaction.objects.filter(
            emoji=self.emoji,
            content_type=self.content_type,
            object_id=self.object_id,
            created_by=self.created_by,
        ).exists():
            raise ReactionExists()
        elif (
            Reaction.objects.filter(
                content_type=self.content_type,
                object_id=self.object_id,
                created_by=self.created_by,
            ).count()
            >= REACTION_COUNT_LIMIT
        ):
            raise TooManyReactions()
        else:
            super(Reaction, self).save(*args, **kwargs)

    def delete(self, using=None, force=False):
        super().delete(using, force=True)
