from django.conf import settings
from django.db.models import CharField
from rest_framework.exceptions import ValidationError

from lego.apps.content.models import Content
from lego.apps.files.models import FileField
from lego.apps.permissions.models import ObjectPermissionsModel
from lego.utils.models import BasisModel
from lego.utils.youtube_validator import youtube_validator


class Article(Content, BasisModel, ObjectPermissionsModel):
    cover = FileField(related_name="article_covers")
    youtube_url = CharField(
        max_length=200, default="", validators=[youtube_validator], blank=True
    )

    class Meta:
        abstract = False

    def get_absolute_url(self):
        return f"{settings.FRONTEND_URL}/articles/{self.id}/"
