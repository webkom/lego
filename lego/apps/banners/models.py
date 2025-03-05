from django.db import models

from lego.apps.banners.permissions import BannersPermissionHandler
from lego.utils.models import BasisModel


class Banners(BasisModel):
    header = models.CharField()
    subheader = models.CharField()
    link = models.CharField()
    current_public = models.BooleanField(default=False, null=False, blank=False)
    current_private = models.BooleanField(default=False, null=False, blank=False)

    class Meta:
        permission_handler = BannersPermissionHandler()
        indexes = [
            models.Index(fields=["current_public"]),
            models.Index(fields=["current_private"]),
        ]
