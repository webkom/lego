from django.db import models
from django.db.models import Q

from lego.apps.banners.constants import BANNER_COLORS_CHOICES, BANNER_COLORS_DEFAULT
from lego.apps.banners.permissions import BannersPermissionHandler
from lego.utils.models import BasisModel


class Banners(BasisModel):
    header = models.CharField(max_length=256)
    subheader = models.CharField(max_length=256, null=True)
    link = models.CharField(max_length=512, null=True, blank=True)
    current_public = models.BooleanField(default=False)
    current_private = models.BooleanField(default=False)
    countdown_end_date = models.DateTimeField(null=True, blank=True)
    countdown_end_message = models.CharField(max_length=256, null=True, blank=True)
    color = models.CharField(
        choices=BANNER_COLORS_CHOICES, default=BANNER_COLORS_DEFAULT
    )

    class Meta:
        permission_handler = BannersPermissionHandler()
        indexes = [
            models.Index(fields=["current_public"]),
            models.Index(fields=["current_private"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["current_public"],
                condition=Q(current_public=True),
                name="unique_current_public",
            ),
            models.UniqueConstraint(
                fields=["current_private"],
                condition=Q(current_private=True),
                name="unique_current_private",
            ),
        ]

    def __str__(self):
        status = []
        if self.current_public:
            status.append("public")
        if self.current_private:
            status.append("private")
        status_str = f" [{', '.join(status)}]" if status else ""
        return f"{self.header}{status_str}"
