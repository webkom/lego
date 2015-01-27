# -*- coding: utf--8 -*-
from lego.users.models import User


class TestMixin:
    def test_author(self):
        self.user1 = User.objects.get(id=1)
        self.user2 = User.objects.get(id=2)
        self.item = self.model.objects.get(id=1)

        self.assertEqual(self.item.author, self.user1)
        self.assertNotEqual(self.item.author, self.user2)

