from django.core.validators import validate_slug
from django.db import models


class Tag(models.Model):
    tag = models.CharField(max_length=64, primary_key=True, validators=[validate_slug])
