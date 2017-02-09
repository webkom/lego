from django.db import models
from django.utils.crypto import get_random_string


class ICalToken(models.Model):
    user = models.ForeignKey('users.User')
    token = models.CharField(
        max_length=64, default=lambda: get_random_string(length=64), db_index=True
    )
