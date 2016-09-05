from django.test import TestCase

from lego.apps.search.search_indexes import SearchTestModelIndex


class SearchIndexTestCase(TestCase):
    pass


class SearchTestModelIndexTestCase(TestCase):

    fixtures = ['search_test_model.yaml']

    def setUp(self):
        self.index = SearchTestModelIndex()

    def test_get_index_queryset(self):
        """
        Test the queryset the index returns.
        """
        test_objects = self.index.index_queryset()
        self.assertEquals(test_objects[0].title, 'Webkom Søk')
        self.assertEquals(test_objects.count(), 2)
        test_objects[0].delete()
