from django.test import TestCase

from lego.apps.companies.filters import CompanyFilterSet
from lego.apps.companies.models import Company


class CompanyFilterSetTestCase(TestCase):
    fixtures = ["test_abakus_groups.yaml", "test_users.yaml", "test_companies.yaml"]

    def setUp(self):
        self.filter_set = CompanyFilterSet
        self.queryset = Company.objects.all()

    def test_filter_search_empty(self):
        """Test that empty search returns full queryset"""
        filtered = self.filter_set({"search": ""}, queryset=self.queryset).qs
        self.assertEqual(filtered.count(), self.queryset.count())

    def test_filter_search_name(self):
        """Test search filtering by company name"""
        filtered = self.filter_set({"search": "Facebook"}, queryset=self.queryset).qs
        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first().name, "Facebook")

    def test_filter_search_description(self):
        """Test search filtering by company description"""
        filtered = self.filter_set(
            {"search": "webkom er webkom"}, queryset=self.queryset
        ).qs
        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first().name, "Webkom")

    def test_filter_search_case_insensitive(self):
        """Test that search is case insensitive"""
        filtered = self.filter_set({"search": "facebook"}, queryset=self.queryset).qs
        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first().name, "Facebook")

    def test_filter_inactive_default(self):
        """Test that by default only active companies are shown"""
        company = Company.objects.get(name="Facebook")
        company.active = False
        company.save()

        filtered = self.filter_set({"show_inactive": False}, queryset=self.queryset).qs
        self.assertNotIn(company, filtered)

    def test_filter_show_inactive(self):
        """Test that inactive companies can be shown when requested"""
        company = Company.objects.get(name="Facebook")
        company.active = False
        company.save()

        filtered = self.filter_set({"show_inactive": True}, queryset=self.queryset).qs
        self.assertIn(company, filtered)
