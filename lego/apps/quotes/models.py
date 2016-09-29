from basis.models import BasisModel
from django.db import models
from lego.apps.content.models import Content
from lego.apps.likes.models import Likeable

from lego.apps.permissions.models import ObjectPermissionsModel
from lego.apps.users.models import AbakusGroup, User


class Quote(Likeable, Content, BasisModel, ObjectPermissionsModel):
    source = models.CharField(max_length=255)
    approved = models.BooleanField(default=False)
    permission_groups = models.ManyToManyField(AbakusGroup)

    def __str__(self):
        return self.title

    def approve(self):
        self.approved = True
        self.save()

    def unapprove(self):
        self.approved = False
        self.save()
