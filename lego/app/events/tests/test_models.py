from django.test import TestCase
from django.utils.text import slugify

from lego.app.content.tests import ContentTestMixin
from lego.app.events.models import Event
from lego.app.events.views.events import EventViewSet


class EventTest(TestCase, ContentTestMixin):

    fixtures = ['initial_abakus_groups.yaml', 'initial_users.yaml',
                'test_users.yaml', 'test_events.yaml']

    model = Event
    ViewSet = EventViewSet


class EventMethodTest(TestCase):
    fixtures = ['test_users.yaml', 'test_events.yaml']

    def setUp(self):
        self.event = Event.objects.get(pk=1)

    def test_str(self):
        self.assertEqual(str(self.event), self.event.title)

    def test_slug(self):
        self.assertEqual(slugify(self.event.title), self.event.slug())
