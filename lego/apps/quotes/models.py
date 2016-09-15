from basis.models import BasisModel
from django.db import models
from lego.apps.content.models import Content

from lego.apps.permissions.models import ObjectPermissionsModel
from lego.apps.users.models import AbakusGroup, User


class Quote(Content, BasisModel, ObjectPermissionsModel):
    source = models.CharField(max_length=255)
    approved = models.BooleanField(default=False)
    permission_groups = models.ManyToManyField(AbakusGroup)

    def __str__(self):
        return self.title

    @property
    def likes(self):
        return QuoteLike.objects.filter(quote=self).count()

    def has_liked(self, user):
        return QuoteLike.objects.filter(user=user, quote=self).exists()

    def approve(self):
        self.approved = True
        self.save()

    def unapprove(self):
        self.approved = False
        self.save()

    def like(self, user):
        return QuoteLike.objects.create(user=user, quote=self)

    def unlike(self, user):
        QuoteLike.objects.filter(user=user, quote=self).delete()


class QuoteLike(BasisModel):
    user = models.ForeignKey(User)
    quote = models.ForeignKey(Quote)

    class Meta:
        unique_together = ('user', 'quote')
