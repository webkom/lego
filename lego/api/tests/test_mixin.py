from unittest import mock

from django.conf import settings
from django.http import Http404
from django.test import TestCase
from rest_framework.viewsets import GenericViewSet

from lego.api import mixins


class ViewSetMock(mixins.NestedViewSetMixin, GenericViewSet):

    queryset = mock.Mock()


class NestedViewSetMixinTestCase(TestCase):

    def setUp(self):
        self.view = ViewSetMock()

    @mock.patch('lego.api.mixins.NestedViewSetMixin.filter_queryset_by_parents_lookups')
    def test_get_queryset(self, mock_filter_queryset_by_parents_lookups):
        self.view.get_queryset()
        mock_filter_queryset_by_parents_lookups.assert_called_once_with(self.view.queryset)

    @mock.patch('lego.api.mixins.NestedViewSetMixin.get_parents_query_dict', return_value={})
    def test_queryset_filter_no_parents(self, mock_get_parents_query_dict):
        self.assertEquals(self.view.get_queryset(), self.view.queryset)

    @mock.patch('lego.api.mixins.NestedViewSetMixin.get_parents_query_dict', return_value={
        'event': 1})
    def test_queryset_filter_invalid(self, mock_get_parents_query_dict):
        self.view.queryset.filter.side_effect = ValueError
        self.assertRaises(Http404, self.view.get_queryset)

    @mock.patch('lego.api.mixins.NestedViewSetMixin.get_parents_query_dict', return_value={
        'event': 1})
    def test_queryset_filter_by_parents(self, mock_get_parents_query_dict):
        self.view.get_queryset()
        self.view.queryset.filter.assert_called_once_with(event=1)

    def test_get_parents_query_dict(self):
        prefix = settings.PARENT_LOOKUP_PREFIX
        self.view.kwargs = {
            'request': None,
            'mock_value': 1,
            '{0}event'.format(prefix): 2,
            '{0}pool'.format(prefix): 3
        }
        self.assertDictEqual(self.view.get_parents_query_dict(), {
            'event': 2,
            'pool': 3
        })
