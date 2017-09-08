from django.db import models

from lego.apps.tags.validators import validate_tag


class Tag(models.Model):
    tag = models.CharField(max_length=64, primary_key=True, validators=[validate_tag])
