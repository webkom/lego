from rest_framework.test import APITestCase

import lego.apps.events.tests.test_events_api as event_api
from lego.apps.tags.models import Tag
from lego.apps.users.models import User


class TagsTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_tags_data.yaml',
                'initial_tags.yaml']

    def setUp(self):
        user = User.objects.get(pk=1)
        self.client.force_authenticate(user)

    def test_add_existing_tag(self):
        pk = 1
        event = self.client.get(event_api._get_detail_url(pk))
        event_data = event.data
        # Make sure that we're not adding a tag which is there already.
        # The simplest way to do this is to ensure that the event has no tags.
        self.assertEquals(len(event_data.pop('tags')), 0)
        tag = Tag.objects.first()
        event_data['tags'] = [tag.tag]
        res = self.client.put(event_api._get_detail_url(pk), event_data)
        self.assertEquals(res.status_code, 200)
        self.assertTrue(tag.tag in res.data.pop('tags'))

    def test_remove_tag(self):
        pk = 2
        event = self.client.get(event_api._get_detail_url(pk))
        event_data = event.data
        tags = event_data.pop('tags')
        removed = tags.pop()
        event_data['tags'] = tags
        res = self.client.put(event_api._get_detail_url(pk), event_data)
        self.assertEquals(res.status_code, 200)
        self.assertFalse(removed in res.data.pop('tags'))

    def test_add_duplicate_tag(self):
        pass

    def test_add_new_tag(self):
        pk = 1
        event = self.client.get(event_api._get_detail_url(pk))
        event_data = event.data

        tag = 'ayyy-totaly-unique123'
        self.assertIsNone(Tag.objects.filter(tag=tag).first())

        event_data['tags'] = [tag]
        res = self.client.put(event_api._get_detail_url(pk), event_data)
        print(res.data)
        self.assertEquals(res.status_code, 200)
        self.assertTrue(tag in res.data.pop('tags'))
        self.assertIsNotNone(Tag.objects.filter(tag=tag).first())
