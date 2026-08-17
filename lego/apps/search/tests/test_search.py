from rest_framework import status

from lego.apps.flatpages.models import Page
from lego.apps.flatpages.search_indexes import PageModelIndex
from lego.apps.users.models import User
from lego.apps.users.search_indexes import UserIndex
from lego.utils.test_utils import BaseAPITestCase, BaseTestCase


class SearchIndexTestCase(BaseTestCase):
    def search(self, query):
        return list(PageModelIndex().search(query))

    def test_search_matches_exact_words(self):
        page = Page.objects.create(
            title="Komiteene i Abakus", content="Oversikt over komiteene"
        )
        Page.objects.create(title="Kjellerne", content="Om kjellerne")

        self.assertEqual(self.search("komiteene"), [page])

    def test_search_matches_norwegian_word_forms(self):
        page = Page.objects.create(
            title="Bedriftene kommer", content="Informasjon til studenter"
        )

        # "bedrift" should match "Bedriftene" through norwegian stemming.
        self.assertEqual(self.search("bedrift"), [page])
        self.assertEqual(self.search("bedriften"), [page])

    def test_search_ranks_title_hits_over_content_hits(self):
        content_hit = Page.objects.create(
            title="Praktisk informasjon",
            content="Generalforsamlingen holdes hvert år",
        )
        title_hit = Page.objects.create(
            title="Generalforsamling", content="Praktisk informasjon"
        )

        self.assertEqual(self.search("generalforsamling"), [title_hit, content_hit])

    def test_search_does_not_match_unrelated_query(self):
        Page.objects.create(title="Komiteene i Abakus", content="Oversikt")

        self.assertEqual(self.search("fondet"), [])


class AutocompleteIndexTestCase(BaseTestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="aleksandern",
            first_name="Aleksander",
            last_name="Nygaard",
            email="aleksandern@abakus.no",
        )
        self.other_user = User.objects.create(
            username="martah",
            first_name="Marta",
            last_name="Hansen",
            email="martah@abakus.no",
        )

    def autocomplete(self, query):
        return list(UserIndex().autocomplete(query))

    def test_autocomplete_matches_prefix(self):
        self.assertEqual(self.autocomplete("alek"), [self.user])

    def test_autocomplete_matches_words_across_fields(self):
        # First name prefix + last name prefix.
        self.assertEqual(self.autocomplete("aleks nyg"), [self.user])

    def test_autocomplete_matches_typos_with_trigram_similarity(self):
        self.assertEqual(self.autocomplete("aleksender"), [self.user])

    def test_autocomplete_does_not_match_unrelated_query(self):
        self.assertEqual(self.autocomplete("zxqwerty"), [])

    def test_autocomplete_handles_query_with_only_special_chars(self):
        self.assertEqual(self.autocomplete("&:*|"), [])

    def test_autocomplete_ranks_prefix_matches_above_fuzzy_matches(self):
        # Scores higher on whole-query trigram similarity than the exact match,
        # but does not match the per-word prefixes "aleks:* & nyg:*".
        fuzzy_only = User.objects.create(
            username="aleksb",
            first_name="Aleks",
            last_name="Bergman",
            email="aleksb@abakus.no",
        )

        self.assertEqual(self.autocomplete("aleks nyg"), [self.user, fuzzy_only])


class SearchAPITestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_users.yaml"]

    def setUp(self):
        self.page = Page.objects.create(
            title="Webkomiteen", content="Webkom drifter abakus.no", require_auth=False
        )
        self.client.force_authenticate(User.objects.get(pk=1))

    def test_search_endpoint(self):
        response = self.client.post(
            "/api/v1/search-search/",
            {"query": "webkomiteen", "types": ["flatpages.page"]},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], self.page.pk)
        self.assertEqual(results[0]["contentType"], "flatpages.page")
        self.assertEqual(results[0]["title"], "Webkomiteen")
        # The old backends injected a literal "text" placeholder that clobbered
        # real result fields named text.
        self.assertNotIn("text", results[0])

    def test_search_endpoint_deduplicates_types(self):
        response = self.client.post(
            "/api/v1/search-search/",
            {"query": "webkomiteen", "types": ["flatpages.page", "flatpages.page"]},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_search_endpoint_rejects_too_long_query(self):
        response = self.client.post(
            "/api/v1/search-search/",
            {"query": "a" * 10_000, "types": ["flatpages.page"]},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_autocomplete_endpoint_rejects_too_long_query(self):
        response = self.client.post(
            "/api/v1/search-autocomplete/",
            {"query": "ab " * 5_000},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_autocomplete_endpoint(self):
        response = self.client.post(
            "/api/v1/search-autocomplete/",
            {"query": "webko", "types": ["flatpages.page"]},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], self.page.pk)
