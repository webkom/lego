from django.conf import settings
from django.db.models import BooleanField, CharField, ManyToManyField

from lego.apps.content.models import Content
from lego.apps.files.models import FileField
from lego.apps.permissions.models import ObjectPermissionsModel
from lego.apps.users.models import User
from lego.utils.models import BasisModel
from lego.utils.youtube_validator import youtube_validator


class Article(Content, BasisModel, ObjectPermissionsModel):
    cover = FileField(related_name="article_covers")
    youtube_url = CharField(
        max_length=200, default="", validators=[youtube_validator], blank=True
    )
    authors = ManyToManyField(User)
    wiggle = BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.pinned:
            for pinned_item in Article.objects.filter(pinned=True).exclude(pk=self.pk):
                pinned_item.pinned = False
                pinned_item.save()
        super().save(*args, **kwargs)

    class Meta:
        abstract = False

    def get_absolute_url(self):
        return f"{settings.FRONTEND_URL}/articles/{self.id}/"
