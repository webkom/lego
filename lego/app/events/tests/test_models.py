# -*- coding: utf8 -*-
from django.test import TestCase
from lego.app.events.models import Event


class CapacityTestCase(TestCase):
    fixtures = ['test_event.yaml']

    def test_capacity(self):
        event = Event.objects.get(pk=1)
        pool_one = event.add_pool("1-2 klasse", 10)
        pool_two = event.add_pool("3-5 klasse", 20)
        capacity = pool_one.size + pool_two.size
        self.assertEqual(capacity, event.capacity_count)