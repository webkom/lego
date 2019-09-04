from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres import fields
from django.db import IntegrityError, models
from rest_framework.exceptions import ValidationError

from lego.apps.emojis.permissions import EmojiPermissionHandler
from lego.utils.managers import BasisModelManager
from lego.utils.models import BasisModel


class Emoji(BasisModel):
    short_code = models.CharField(max_length=40, primary_key=True)
    keywords = fields.ArrayField(models.CharField(max_length=40))
    unicode_string = models.CharField(max_length=24, db_index=True)
    fitzpatrick_scale = models.BooleanField()
    category = models.CharField(max_length=40, db_index=True)
    disabled = models.BooleanField(default=False)

    class Meta:
        permission_handler = EmojiPermissionHandler()
