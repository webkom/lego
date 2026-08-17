from __future__ import annotations

from typing import Any, Sequence

from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
    TrigramWordSimilarity,
)
from django.db.models import (
    BooleanField,
    Expression,
    ExpressionWrapper,
    F,
    Model,
    Q,
    QuerySet,
    TextField,
    Value,
)
from django.db.models.expressions import Combinable
from django.db.models.functions import Concat
from rest_framework.serializers import Serializer

from structlog import get_logger

log = get_logger()

SEARCH_CONFIG = "norwegian"


class SearchIndex:
    """
    Base class for search indexes. Implement this class to make a model searchable. Remember to
    use the register function to register the index. Searches query the live database rows using
    Postgres full text search, so there is no separate index to keep in sync.
    """

    queryset: QuerySet | None = None
    serializer_class: type[Serializer] | None = None
    fallback_to_autocomplete: bool = False

    search_fields: Sequence[str] | None = None
    autocomplete_fields: Sequence[str] | None = None
    result_fields: Sequence[str] | None = None
    autocomplete_result_fields: Sequence[str] = ()

    # Secondary orderings applied after rank/similarity, e.g. ("-start_time",)
    search_ordering: tuple[str, ...] = ()
    autocomplete_ordering: tuple[str, ...] = ()

    # Minimum trigram word similarity for a fuzzy autocomplete match.
    autocomplete_similarity_threshold: float = 0.4

    def get_queryset(self) -> QuerySet:
        """
        Get the queryset that should be searched. Override this method or set a queryset
        attribute on this class.
        """
        queryset = self.queryset

        if queryset is None:
            raise NotImplementedError(
                f"You must provide a 'get_queryset' method or queryset attribute for the {self} "
                f"index."
            )
        return queryset

    def get_model(self) -> type[Model]:
        """
        Get the model this index is bound to.
        """
        queryset = self.get_queryset()
        return queryset.model

    def get_serializer_class(self) -> type[Serializer]:
        """
        Override this method or set the serializer_class attribute on the class to define the
        serializer.
        """
        serializer_class = self.serializer_class
        if serializer_class is None:
            raise NotImplementedError(
                "You must provide a 'get_serializer_class' function or a "
                f"serializer_class attribute for the {self} index"
            )
        return serializer_class

    def get_result_fields(self) -> Sequence[str]:
        """
        Returns a list of fields attached to the search result.
        """
        result_fields = self.result_fields
        if result_fields is None:
            raise NotImplementedError(
                "You must provide a 'get_result_fields' function or a "
                f"result_fields attribute for the {self} index"
            )
        return result_fields

    def get_autocomplete_result_fields(self) -> Sequence[str]:
        """
        Returns a list of fields attached to the autocomplete result.
        """
        return self.autocomplete_result_fields

    def get_serializer(self, *args: Any, **kwargs: Any) -> Serializer:
        """
        Return the serializer with args and kwargs.
        """
        serializer_class = self.get_serializer_class()
        return serializer_class(*args, **kwargs)

    def clean_query(self, query: str) -> str:
        """
        Clean search query to prepare for pg search.
        Removes characters like &, | and other chars used in pg full text search.
        """
        chars = ["&", "*", ":", "@", "|", "<", ">", "!", "(", ")", "'", "\\"]
        for char in chars:
            query = query.replace(char, "")

        return query

    def _build_search_vector(
        self, search_fields: Sequence[str], config: str = SEARCH_CONFIG
    ) -> Expression:
        """
        Build a weighted search vector: the first field (usually the title) is weighted highest.
        """
        vector: Expression = SearchVector(search_fields[0], weight="A", config=config)
        if search_fields[1:]:
            vector = vector + SearchVector(
                *search_fields[1:], weight="B", config=config
            )
        return vector

    def search(self, query: str) -> QuerySet:
        """
        Full text search on the model using the database. The Norwegian config stems both the
        indexed text and the query, and results are ordered by relevance rank with
        `search_ordering` as tiebreaker. Only works for PostgreSQL.
        """
        search_fields = self.search_fields
        if search_fields is None:
            if self.fallback_to_autocomplete:
                return self.autocomplete(query)
            raise NotImplementedError(
                "You must provide a 'search_fields' attribute or override this method"
            )

        vector = self._build_search_vector(search_fields)
        search_query = SearchQuery(query, search_type="websearch", config=SEARCH_CONFIG)
        queryset: QuerySet = (
            self.get_queryset()
            .annotate(lego_search=vector, lego_rank=SearchRank(vector, search_query))
            .filter(lego_search=search_query)
            .order_by("-lego_rank", *self.search_ordering, "-pk")
        )
        return queryset

    def autocomplete(self, query: str) -> QuerySet:
        """
        Autocomplete on the model using the database. Matches per-word prefixes across the
        autocomplete fields (so "aleks nyg" matches first name + last name) or, for typo
        tolerance, trigram word similarity. Results are ordered by similarity with
        `autocomplete_ordering` as tiebreaker. Only works for PostgreSQL.
        """
        autocomplete_fields = self.autocomplete_fields
        if autocomplete_fields is None:
            raise NotImplementedError(
                "You must provide a 'autocomplete_fields' attribute or override this method"
            )

        cleaned = self.clean_query(query)
        words = cleaned.split()
        if not words:
            return self.get_queryset().none()

        # Names and titles should not be stemmed, so use the simple config for prefix matching.
        vector = SearchVector(*autocomplete_fields, config="simple")
        prefix_query = SearchQuery(
            " & ".join(f"{word}:*" for word in words),
            search_type="raw",
            config="simple",
        )

        combined: Combinable
        if len(autocomplete_fields) == 1:
            combined = F(autocomplete_fields[0])
        else:
            expressions: list[Combinable] = []
            for field in autocomplete_fields:
                if expressions:
                    expressions.append(Value(" "))
                expressions.append(F(field))
            combined = Concat(*expressions, output_field=TextField())

        queryset: QuerySet = (
            self.get_queryset()
            .annotate(
                lego_search=vector,
                lego_similarity=TrigramWordSimilarity(cleaned, combined),
            )
            # Exact prefix matches must rank above fuzzy-only matches: trigram
            # similarity alone can score a typo-ish hit higher than the match the
            # user is literally typing.
            .annotate(
                lego_prefix_match=ExpressionWrapper(
                    Q(lego_search=prefix_query), output_field=BooleanField()
                )
            )
            .filter(
                Q(lego_search=prefix_query)
                | Q(lego_similarity__gt=self.autocomplete_similarity_threshold)
            )
            .order_by(
                "-lego_prefix_match",
                "-lego_similarity",
                *self.autocomplete_ordering,
                "-pk",
            )
        )
        return queryset
