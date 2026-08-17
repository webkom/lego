from __future__ import annotations

from typing import Iterable

from django.db.models import Model

from . import registry
from .index import SearchIndex


class SearchBackend:
    """
    Postgres-backed search. Queries the live database rows through the registered search
    indexes, so there is no separate search index to maintain or keep in sync.
    """

    name = "postgres"

    max_results = 10

    def get_search_index(self, content_type: str) -> SearchIndex | None:
        """
        Return the search_index registered for a content_type.
        """
        return registry.get_content_type_index(content_type)

    def _search(
        self,
        query: str,
        content_types: Iterable[str] | None,
        autocomplete: bool = False,
    ) -> list[Model]:
        # Materialize and dedupe: duplicate types in the request must not multiply
        # queries or skew the interleaving below.
        content_types = list(dict.fromkeys(content_types or ()))
        if not content_types:
            content_types = list(registry.index_registry.keys())

        max_results_per_type = self.max_results
        results_by_content_type: dict[str, list[Model]] = {
            content_type: [] for content_type in content_types
        }
        for content_type in content_types:
            search_index = self.get_search_index(content_type)
            if search_index is None:
                continue
            if autocomplete:
                db_results = search_index.autocomplete(query)[:max_results_per_type]
            else:
                db_results = search_index.search(query)[:max_results_per_type]
            results_by_content_type[content_type] = list(db_results)

        # Interleave results so results are not only of one type if there are many matches
        results = []
        for _ in range(max_results_per_type):
            for content_type in content_types:
                if len(results_by_content_type[content_type]):
                    results.append(results_by_content_type[content_type].pop(0))

        return results

    def search(
        self,
        query: str,
        content_types: list[str] | None = None,
        filters: dict | None = None,
    ) -> list[Model]:
        return self._search(query, content_types)

    def autocomplete(
        self, query: str, content_types: list[str] | None = None
    ) -> list[Model]:
        return self._search(query, content_types, autocomplete=True)

    def serialize_object(self, object: Model, search_type: str) -> dict:
        from lego.utils.content_types import instance_to_content_type_string

        content_type = instance_to_content_type_string(object)
        search_index = self.get_search_index(content_type)
        if search_index is None:
            raise ValueError(f"No search index registered for {content_type}")
        serializer = search_index.get_serializer(object)
        fields = (
            search_index.get_autocomplete_result_fields()
            if search_type == "autocomplete"
            else search_index.get_result_fields()
        )
        result = {field: serializer.data[field] for field in fields}
        result.update({"id": object.pk, "content_type": content_type})
        return result

    def serialize(
        self, objects: list[Model], search_type: str = "autocomplete"
    ) -> list[dict]:
        return [
            self.serialize_object(object, search_type)
            for object in objects[: self.max_results]
        ]

    def get_django_object(self, el: Model) -> Model:
        return el


current_backend = SearchBackend()
