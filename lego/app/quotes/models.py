from basis.models import BasisModel
from django.db import models

from lego.permissions.models import ObjectPermissionsModel
from lego.users.models import User


class Quote(ObjectPermissionsModel):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(User)
    text = models.TextField()
    source = models.CharField(max_length=255)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    @property
    def likes(self):
        return QuoteLike.objects.filter(quote=self).count()

    def has_liked(self, user):
        return bool(QuoteLike.objects.filter(user=user, quote=self))

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
    like_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'quote')
