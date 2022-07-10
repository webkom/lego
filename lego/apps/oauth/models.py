from django.db import models

from oauth2_provider.models import AbstractApplication

from .permissions import APIApplicationPermissionHandler


class APIApplicationManager(models.Manager):
    def get_by_natural_key(self, client_id):
        return self.get(client_id=client_id)


class APIApplication(AbstractApplication):

    objects = APIApplicationManager()

    description = models.CharField(
        "application description", max_length=100, blank=True
    )

    def natural_key(self):
        return (self.client_id,)

    class Meta:
        permission_handler = APIApplicationPermissionHandler()
