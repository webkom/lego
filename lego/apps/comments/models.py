from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from lego.apps.comments.permissions import CommentPermissionHandler
from lego.apps.content.fields import ContentField
from lego.apps.reactions.models import Reaction
from lego.utils.managers import BasisModelManager
from lego.utils.models import BasisModel


class CommentManager(BasisModelManager):
    def get_queryset(self):
        return super().get_queryset().select_related("created_by")


class Comment(BasisModel):
    text = ContentField(allow_images=False, null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey()
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)
    reactions = GenericRelation(Reaction)

    objects = CommentManager()  # type: ignore

    class Meta:
        ordering = ("created_at",)
        permission_handler = CommentPermissionHandler()

    def delete(self):
        if Comment.objects.filter(parent=self).exists():
            self.created_by = None
            self.text = None
            self.save()
        else:
            super(Comment, self).delete(force=True)

    def get_reactions_grouped(self, user):
        grouped = {}
        for reaction in self.reactions.all():
            if reaction.emoji.pk not in grouped:
                grouped[reaction.emoji.pk] = {
                    "emoji": reaction.emoji.pk,
                    "unicode_string": reaction.emoji.unicode_string,
                    "count": 0,
                    "has_reacted": False,
                    "reaction_id": None,
                }

            grouped[reaction.emoji.pk]["count"] += 1

            if reaction.created_by == user:
                grouped[reaction.emoji.pk]["has_reacted"] = True
                grouped[reaction.emoji.pk]["reaction_id"] = reaction.id

        return sorted(grouped.values(), key=lambda kv: kv["count"], reverse=True)

    def __str__(self):
        return self.text

    @property
    def content_self(self):
        return f"{self._meta.app_label}.{self._meta.model_name}-{self.pk}"
