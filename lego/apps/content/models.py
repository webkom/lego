from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.text import slugify

from lego.apps.comments.models import Comment
from lego.apps.users.models import User


class Content(models.Model):
    class Meta:
        abstract = True

    title = models.CharField(max_length=255)
    author = models.ForeignKey(User)
    description = models.TextField()
    text = models.TextField(blank=True)
    comments = GenericRelation(Comment)
    slug = models.SlugField(null=True, unique=True)

    @property
    def likes(self):
        return ContentLike.objects.filter(content=self).count()

    def has_liked(self, user):
        return ContentLike.objects.filter(user=user, content=self).exists()

    def like(self, user):
        return ContentLike.objects.create(user=user, content=self)

    def unlike(self, user):
        ContentLike.objects.filter(user=user, content=self).delete()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.slug:
            self.slug = slugify('{}-{}'.format(self.id, self.title))
            self.save()

    def __str__(self):
        return self.title + '(by: {})'.format(self.author)

    @property
    def comment_target(self):
        return '{0}.{1}-{2}'.format(self._meta.app_label, self._meta.model_name, self.pk)


class ContentLike(models.Model):
    user = models.ForeignKey(User)
    content = models.ForeignKey(Content)

    class Meta:
        unique_together = ('user', 'content')
