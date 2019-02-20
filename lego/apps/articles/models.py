from django.conf import settings
from django.db.models import URLField
from django.core.validators import URLValidator

from lego.apps.content.models import Content
from lego.apps.files.models import FileField
from lego.apps.permissions.models import ObjectPermissionsModel
from lego.utils.models import BasisModel

from rest_framework.exceptions import ValidationError


class Article(Content, BasisModel, ObjectPermissionsModel):
    cover = FileField(related_name="article_covers")
    youtube_url = URLField(default="")

    class Meta:
        abstract = False

    def get_absolute_url(self):
        return f"{settings.FRONTEND_URL}/articles/{self.id}/"
