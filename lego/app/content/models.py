# -*- coding: utf--8 -*-
from django.db import models
from lego.permissions.models import ObjectPermissionsModel
from lego.users.models import User
from rest_framework.test import APIRequestFactory


class TestMixin(models.Model):
    fixtures = ['initial_abakus_groups.yaml', 'initial_users.yaml',
                'test_users.yaml', 'test_articles.yaml']

    def do_test(self):
        self.setUp()
        self.testAuthor()
        self.testCanView()

    def setUp(self):
        self.user1 = User.objects.get(id=1)
        self.user2 = User.objects.get(id=2)
        self.item = self.model.objects.get(id=1)

        self.factory = APIRequestFactory()
        self.request = self.factory.get('/api/articles')
        self.view = self.ViewSet.as_view({'get': 'retrieve'})

    def testAuthor(self):
        self.assertEqual(self.item.author, self.user1)
        self.assertNotEqual(self.item.author, self.user2)

    def testCanView(self):
        response = self.view(self.factory.get('/api/articles/1'),
                             pk=self.article.pk, user=self.user1)
        self.assertEqual(response.status_code, 404)



class Content(ObjectPermissionsModel):
    class Meta:
        abstract = True

    title = models.CharField(max_length=255)
    author = models.ForeignKey(User, editable=False, null=True)
    ingress = models.TextField()
    text = models.TextField(blank=True)

    def __str__(self):
        return self.title + '(by: {})'.format(self.author)
