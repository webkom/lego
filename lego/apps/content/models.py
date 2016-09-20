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

    def save(self, *args, **kwargs):
        if not self.author:
            self.author = self.created_by
        super().save(*args, **kwargs)


class SlugContent(Content):
    slug_length = 50
    slug = models.SlugField(null=True, unique=True, max_length=slug_length)

    class Meta:
        abstract = True

    def generate_slug(self):
        slug = slugify('{}-{}'.format(self.id, self.title))
        if len(slug) <= self.slug_length:
            return slug

        if slug[self.slug_length] == '-':
            return slug[0:self.slug_length]

        slug = slug[0:self.slug_length]
        slice_index = slug.rindex('-')
        return slug[0:slice_index]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_slug()
            self.save()
