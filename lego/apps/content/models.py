from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.text import slugify

from lego.apps.comments.models import Comment


class Content(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    text = models.TextField(blank=True)
    comments = GenericRelation(Comment)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    @property
    def comment_target(self):
        return '{0}.{1}-{2}'.format(self._meta.app_label, self._meta.model_name, self.pk)


class SlugContent(Content):
    slug = models.SlugField(null=True, unique=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.slug:
            self.slug = slugify('{}-{}'.format(self.id, self.title))
            self.save()
