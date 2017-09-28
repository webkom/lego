from django.db import models
from oauth2_provider.models import AbstractApplication

from .permissions import APIApplicationPermissionHandler


class APIApplication(AbstractApplication):
    description = models.CharField('application description', max_length=100, blank=True)

    class Meta:
        permission_handler = APIApplicationPermissionHandler()
