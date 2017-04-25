from django.core.cache import cache

from lego.apps.events.models import Event
from lego.apps.users.models import User
from lego.utils.content_types import string_to_model_cls

from . import attr_renderers


class AttrCache:
    """
    The feed contains a lot of content strings, it's heavy to lookup all these values
    on each request. The AttrCache stores the lookups for an small amount of time to reduce the
    load on the database.

    We don't do any invalidation, the cached values is only stored for a small amount of time.
    """

    CACHE_KEY = 'feed_attr_cache_'

    def lookup_cache(self, content_strings):
        """
        Lookup cache keys
        """
        cache_result = cache.get_many(
            [self.CACHE_KEY + content_string for content_string in content_strings]
        )

        # Remove the cache_key prefix
        values = {}
        for key, value in cache_result.items():
            values[key[len(self.CACHE_KEY):]] = value

        return values

    def save_lookups(self, items):
        """
        Cache the items we looked up for a small amount of time.
        """
        cache.set_many(items, timeout=60*5)

    def extract_properties(self, content_type, ids):
        """
        Lookup the values we need from the database.
        Customize the renderers dict to change the values added to the feed.
        """
        model = string_to_model_cls(content_type)

        renderers = {
            User: attr_renderers.render_user,
            Event: attr_renderers.render_event
        }

        rendrer = renderers.get(model)
        if not rendrer:
            return []

        # We need to use getattr on objects because we need to support custom object properties.
        # .values() would have been much better if this wasn't a requirement...
        queryset = model.objects.filter(pk__in=list(ids))
        result = {}

        for instance in queryset:
            data = rendrer(instance)
            data['content_type'] = content_type
            result[f'{content_type}-{instance.pk}'] = data

        return result

    def filter_lookup(self, content_strings):
        """
        Remove invalid content strings and group by content_type for faster lookup.
        Returns a dict: {
            content_type: set(pk's)
        }
        """
        valid = {}

        for content_string in content_strings:
            try:
                content_type, pk = content_string.split('-', maxsplit=1)
                pk = int(pk)
                valid.setdefault(content_type, set()).add(pk)
            except Exception as ex:
                raise Exception('FIKS EXCEPT HER A')

        return valid

    def bulk_lookup(self, content_strings):
        """
        Takes a set of content_strings and returns a list with information about all found items.
        Steps:
            1. Try to find as many keys possible in the cache, we do this first because it's a
            fast operation
            2. Group content_strings by content types
            3. Query the database for all missing items grouped by type
            4. Extract the information we need from each element we found in the database
            5. Cache the values we found in the database
        """
        result = self.lookup_cache(content_strings)

        lookup_required = content_strings - set(result.keys())
        lookup_groups = self.filter_lookup(lookup_required)

        lookups = {}

        for content_type, ids in lookup_groups.items():
            lookup = self.extract_properties(content_type, ids)
            lookups.update(lookup)

        self.save_lookups(lookups)

        result.update(lookups)

        return result
