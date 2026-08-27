from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Model

if TYPE_CHECKING:
    from .index import SearchIndex

"""
The index_registry dict keeps the mapping between SearchIndexes and models.
'players.player': PlayerIndex
"""

index_registry: dict[str, SearchIndex] = {}


def register_search_index(search_index_cls: type[SearchIndex]) -> None:
    """
    Register the search index in our index registry.
    """
    from lego.utils.content_types import instance_to_content_type_string

    search_index = search_index_cls()
    model = search_index.get_model()
    index_registry[instance_to_content_type_string(model)] = search_index


def get_model_index(instance: Model) -> SearchIndex | None:
    """
    Return the index responsible for this instance. Returns None if no index is registered.
    """
    from lego.utils.content_types import instance_to_content_type_string

    return index_registry.get(instance_to_content_type_string(instance))


def get_content_type_index(content_type: str) -> SearchIndex | None:
    """
    Return a index based on a content_type identifier string.
    """
    return index_registry.get(content_type)
