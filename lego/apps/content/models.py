from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import ManyToManyField
from django.utils.text import slugify

from lego.apps.comments.models import Comment
from lego.apps.content.fields import ContentField
from lego.apps.reactions.models import Reaction
from lego.apps.tags.models import Tag


class SlugModel(models.Model):
    """
    An abstract model that can be inherited to add a slug field,
    which is defined by setting self.slug_field to the name
    of the field.
    """

    slug_length = 50
    slug_field = None
    slug = models.SlugField(null=True, unique=True, max_length=slug_length)

    class Meta:
        abstract = True

    def generate_slug(self):
        content = getattr(self, self.slug_field)
        slug = slugify(f"{self.pk}-{content}")
        if len(slug) <= self.slug_length:
            return slug

        if slug[self.slug_length] == "-":
            return slug[0 : self.slug_length]

        slug = slug[0 : self.slug_length]
        slice_index = slug.rindex("-")
        return slug[0:slice_index]

    def save(self, *args, **kwargs) -> None:
        # Save first to generate primary key:
        super().save(*args, **kwargs)
        if not self.slug:
            self.slug = self.generate_slug()
            self.save()


class Content(SlugModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    text = ContentField(allow_images=True)
    comments = GenericRelation(Comment)
    reactions = GenericRelation(Reaction)
    tags = ManyToManyField(Tag, blank=True)
    pinned = models.BooleanField(default=False)

    slug_field = "title"

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

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    @property
    def content_target(self):
        return f"{self._meta.app_label}.{self._meta.model_name}-{self.pk}"
