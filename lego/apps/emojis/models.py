from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres import fields
from django.db import IntegrityError, models
from rest_framework.exceptions import ValidationError

from lego.apps.emojis.exceptions import EmojisExistsInCategory
from lego.apps.emojis.permissions import EmojiPermissionHandler
from lego.apps.files.models import FileField
from lego.utils.managers import BasisModelManager
from lego.utils.models import BasisModel


class Category(BasisModel):
    name = models.CharField(max_length=40, unique=True)
    unicode_string = models.CharField(max_length=24)

    class Meta:
        permission_handler = EmojiPermissionHandler()

    def delete(self, *args, **kwargs):
        if not self.emojis.exists():
            super().delete(*args, **kwargs)
        else:
            raise EmojisExistsInCategory("Emojis exist in Category")


class Emoji(BasisModel):
    short_code = models.CharField(max_length=40, primary_key=True)
    keywords = fields.ArrayField(models.CharField(max_length=40))
    unicode_string = models.CharField(max_length=24, db_index=True, null=True)
    fitzpatrick_scale = models.BooleanField(default=False)
    category = models.ForeignKey(
        Category, related_name="emojis", null=True, on_delete=models.SET_NULL
    )
    approved = models.BooleanField(default=False)
    image = FileField(related_name="emoji_image", null=True)

    class Meta:
        permission_handler = EmojiPermissionHandler()

    def __str__(self):
        return self.short_code

    def enable(self):
        self.disabled = True
        self.save()

    def disable(self):
        self.disabled = False
        self.save()

    def get_absolute_url(self):
        return f"{settings.FRONTEND_URL}/emojis/{self.short_code}/"
