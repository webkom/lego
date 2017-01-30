from django.db import models


class Tag(models.Model):
    tag = models.CharField(max_length=64, primary_key=True)
