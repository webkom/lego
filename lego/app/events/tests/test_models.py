from django.test import TestCase

from lego.app.content.tests import ContentTestMixin
from lego.app.events.models import Event
from lego.app.events.views.events import EventViewSet


class EventTest(TestCase, ContentTestMixin):

    fixtures = ['initial_abakus_groups.yaml', 'initial_users.yaml',
                'test_users.yaml', 'test_events.yaml']

    model = Event
    ViewSet = EventViewSet
