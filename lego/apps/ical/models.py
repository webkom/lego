from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string

from lego.apps.users.models import User


def generate_new_token():
    return get_random_string(length=64)


class ICalToken(models.Model):
    user = models.OneToOneField(User)
    created = models.DateTimeField(auto_now_add=True)
    token = models.CharField(
        max_length=64, default=generate_new_token, db_index=True
    )

    def regenerate(self):
        """ Regenerate the ICalToken """
        self.created = timezone.now()
        self.token = generate_new_token()
        self.save()
