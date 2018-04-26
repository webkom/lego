from django.core.cache import cache
from structlog import get_logger

from lego.utils.content_types import string_to_model_cls

from . import attr_renderers

log = get_logger()


class AttrCache:
    """
    The feed contains a lot of content strings, it's heavy to lookup all these values
    on each request. The AttrCache stores the lookups for an small amount of time to reduce the
    load on the database.

    We don't do any invalidation, the cached values is only stored for a small amount of time.
    """

    CACHE_KEY = 'feed_attr_cache_'

    RENDERS = {
        'users.user': attr_renderers.render_user,
        'events.event': attr_renderers.render_event,
        'meetings.meetinginvitation': attr_renderers.render_meeting_invitation,
        'articles.article': attr_renderers.render_article,
        'notifications.announcement': attr_renderers.render_announcement,
        'gallery.gallerypicture': attr_renderers.render_gallery_picture,
        'users.abakusgroup': attr_renderers.render_abakus_group,
        'events.registration': attr_renderers.render_registration,
        'restricted.restrictedmail': attr_renderers.render_restricted_mail
    }

    RELATED_FIELDS = {'meetings.meetinginvitation': ['meeting']}

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
        cache.set_many(
            {f'{self.CACHE_KEY}{key}': value
             for key, value in items.items()}, timeout=60
        )

    def extract_properties(self, content_type, ids):
        """
        Lookup the values we need from the database.
        Customize the renderers dict to change the values added to the feed.
        """
        model = string_to_model_cls(content_type)

        render = self.RENDERS.get(content_type)
        if not render:
            log.warn('feed_missing_context_render', context=content_type)
            return []

        # We need to use getattr on objects because we need to support custom object properties.
        # .values() would have been much better if this wasn't a requirement...
        related_fields = self.RELATED_FIELDS.get(content_type, [])
        queryset = model.objects.filter(pk__in=list(ids)).select_related(*related_fields)
        result = {}

        for instance in queryset:
            data = render(instance)
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

                if content_type not in self.RENDERS.keys():
                    continue

                valid.setdefault(content_type, set()).add(pk)
            except ValueError:
                pass

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
