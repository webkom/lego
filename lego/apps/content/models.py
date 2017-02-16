import bleach
from bs4 import BeautifulSoup
from django_thumbor import generate_url
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models, transaction
from django.db.models import ManyToManyField
from django.utils.text import slugify

from lego.apps.comments.models import Comment
from lego.apps.reactions.models import Reaction
from lego.apps.tags.models import Tag
from lego.apps.files.models import File


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
        slug = slugify(f'{self.pk}-{content}')
        if len(slug) <= self.slug_length:
            return slug

        if slug[self.slug_length] == '-':
            return slug[0:self.slug_length]

        slug = slug[0:self.slug_length]
        slice_index = slug.rindex('-')
        return slug[0:slice_index]

    def save(self, *args, **kwargs):
        # Save first to generate primary key:
        super().save(*args, **kwargs)
        if not self.slug:
            self.slug = self.generate_slug()
            self.save()


class Content(SlugModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    text = models.TextField(blank=True)
    comments = GenericRelation(Comment)
    reactions = GenericRelation(Reaction)
    images = ManyToManyField(File, blank=True)
    tags = ManyToManyField(Tag, blank=True)
    slug_field = 'title'

    @property
    def content(self):
        text = BeautifulSoup(self.text, 'html.parser')
        for image in text.find_all('img'):
            image['src'] = generate_url(image.get('data-file-key'))
        return str(text)

    @content.setter
    def content(self, value):
        images = []
        safe_content = bleach.clean(
            value,
            tags=[
                'p', 'b', 'i', 'u', 'h1', 'h2', 'code', 'pre', 'blockquote', 'strong'
                'strong', 'strike', 'ul', 'cite', 'li', 'em', 'hr', 'img', 'div', 'a'
            ],
            attributes=['data-file-key', 'data-username', 'data-block-type', 'href'],
            strip=True
        )
        text = BeautifulSoup(safe_content, 'html.parser')
        for image in text.find_all('img'):
             images.append(image.get('data-file-key'))
        if images:
             self.images = images
        self.text = str(text)


    @property
    def reactions_grouped(self):
        grouped = {}
        for reaction in self.reactions.all():
            if reaction.type_id not in grouped:
                grouped[reaction.type_id] = {
                    'type': reaction.type_id,
                    'count': 0,
                    'users': []
                }
            grouped[reaction.type_id]['count'] += 1
            grouped[reaction.type_id]['users'].append(reaction.created_by)
        return grouped.values()


    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.pk:
                images = self.images
                tags = self.tags
                self.images = None
                self.tags = None
                super().save(*args, **kwargs)
                self.images = images
                self.tags = tags
            return super().save(*args, **kwargs)

    @property
    def comment_target(self):
        return f'{self._meta.app_label}.{self._meta.model_name}-{self.pk}'
