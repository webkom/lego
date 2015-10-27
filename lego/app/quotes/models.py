# -*- coding: utf--8 -*-
from basis.models import BasisModel
from django.db import models

from lego.permissions.models import ObjectPermissionsModel
from lego.users.models import User

from django.utils import timezone


class Quote(ObjectPermissionsModel):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(User)
    quote = models.TextField()
    source = models.CharField(max_length=255)
    approved = models.BooleanField(default=False)
    publish_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def likes(self):
        return QuoteLike.objects.filter(quote=self).count()

    def has_liked(self, user):
        return QuoteLike.objects.all().filter(user=user, quote=self).count() == 1

    def can_like(self, user):
        quote_like = QuoteLike.objects.all().filter(user=user, quote=self)
        return self.is_approved() and quote_like.count() == 0

    def can_unlike(self, user):
        quote_like = QuoteLike.objects.all().filter(user=user, quote=self)
        return self.is_approved() and quote_like.count() == 1

    def approve(self):
        self.approved = True
        self.save()

    def unapprove(self):
        self.approved = False
        self.save()

    def is_approved(self):
        return self.approved

    def like(self, user):
        if self.can_like(user=user):
            QuoteLike.objects.create(user=user, quote=self)
            return True
        return False

    def unlike(self, user):
        if self.can_unlike(user=user):
            QuoteLike.objects.filter(user=user, quote=self).delete()
            return True
        return False


class QuoteLike(BasisModel):
    user = models.ForeignKey(User)
    quote = models.ForeignKey(Quote)
    like_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'quote')

    def has_liked(self, user, quote):
        return self.objects.all().filter(user=user, quote=quote).count() > 0

    def number_of_likes(self, quote):
        return self.objects.all().filter(quote=quote).count()

class SortType(BasisModel):
    sort_type = models.CharField(max_length=255)

    def sort_type(self):
        return self.sort_type

    def sort_by_likes(self):
        self.sort_type = 'likes'
        self.save()

    def sort_by_date(self):
        self.sort_type = 'date'
        self.save()