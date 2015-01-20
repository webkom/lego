# -*- coding: utf--8 -*-
from django.db import models
from lego.permissions.models import ObjectPermissionsModel
from lego.users.models import User
from rest_framework.test import APIRequestFactory


class TestMixin:

    def testAuthor(self):
        self.user1 = User.objects.get(id=1)
        self.user2 = User.objects.get(id=2)
        self.item = self.model.objects.get(id=1)

        self.assertEqual(self.item.author, self.user1)
        self.assertNotEqual(self.item.author, self.user2)


class Content(ObjectPermissionsModel):
    class Meta:
        abstract = True

    title = models.CharField(max_length=255)
    author = models.ForeignKey(User, editable=False, null=True)
    ingress = models.TextField()
    text = models.TextField(blank=True)

    def __str__(self):
        return self.title + '(by: {})'.format(self.author)
