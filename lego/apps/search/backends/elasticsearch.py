import certifi
from django.conf import settings
from django.template.loader import render_to_string
from elasticsearch import Elasticsearch, NotFoundError
from elasticsearch.helpers import bulk

from lego.apps.search.backend import SearchBacked


class ElasticsearchBackend(SearchBacked):

    name = 'elasticsearch'

    connection = None

    def set_up(self):
        hosts = getattr(settings, 'ELASTICSEARCH', None)
        if hosts:
            self.connection = Elasticsearch(hosts=settings.ELASTICSEARCH, ca_certs=certifi.where())

    def _index_name(self):
        """
        Return the index target for our queries. We may add more arguments and return different
        indexes based on content_type at a later stage. We need to rewrite the migrate_search and
        rebuild_index management commands when we do this, these commands uses the backend directly.
        """
        return settings.SEARCH_INDEX

    def _bulk(self, actions):
        """
        Execute many operations using the bulk interface.
        """
        return bulk(self.connection, actions, stats_only=True)

    def _index(self, content_type, pk, data):
        """
        Shortcut to index a instance.
        """
        action = {
            '_op_type': 'index',
            '_index': self._index_name(),
            '_type': content_type,
            '_id': pk,
        }
        data.update(action)
        return data

    def _remove(self, content_type, pk):
        """
        Shortcut to create a item removal operation.
        """
        action = {
            '_op_type': 'delete',
            '_index': self._index_name(),
            '_type': content_type,
            '_id': pk,
        }
        return action

    def _clear(self):
        """
        We do a index deletion and creation when we clean a index.
        """
        try:
            self.connection.indices.delete(settings.SEARCH_INDEX)
        except NotFoundError:
            pass
        self.connection.indices.create(settings.SEARCH_INDEX)

    def _search(self, payload, content_types=None):
        types = None
        if content_types:
            types = ','.join(content_types)
        return self.connection.search(settings.SEARCH_INDEX, doc_type=types, body=payload)

    def _suggest(self, payload):
        return self.connection.suggest(payload, index=settings.SEARCH_INDEX)

    def _refresh_template(self, template_name='lego-search'):
        context = {
            'index': self._index_name()
        }
        template = render_to_string('search/elasticsearch/index_template.json', context)
        try:
            self.connection.indices.delete_template(template_name)
        except NotFoundError:
            pass
        return self.connection.indices.put_template(template_name, template)

    def _format_autocomplete(self, content_type, autocomplete_value):
        """
        We use this function to map autocomplete values into a format that elasticsearch
        understands. We use this at index-time.
        """
        if autocomplete_value:
            return {
                'autocomplete': {
                    'input': autocomplete_value,
                    'contexts': {
                        'content_type': content_type
                    }
                }
            }

    def migrate(self):
        """
        The only migration we need is to upload a index template. This is used by ES when the
        index is created.
        """
        self._refresh_template()

    def update_many(self, tuple_list):

        def create_operation(data_tuple):
            content_type, pk, data = data_tuple
            data_fields = dict()

            # Add fields to the operation payload
            data_fields.update(data.get('fields', {}))

            # Add autocomplete to the operation if it exists
            autocomplete = self._format_autocomplete(content_type, data.pop('autocomplete'))
            if autocomplete:
                data_fields.update(autocomplete)

            # Add filter fields
            filter_fields = data.get('filters', {})
            data_fields.update({f'{k}_filter': v for k, v in filter_fields.items()})

            return self._index(content_type, pk, data_fields)

        return self._bulk(map(create_operation, tuple_list))

    def remove_many(self, tuple_list):

        def create_operation(data_tuple):
            content_type, pk = data_tuple
            return self._remove(content_type, pk)

        return self._bulk(map(create_operation, tuple_list))

    def clear(self):
        self._clear()

    def search(self, query, content_types=None, filters=None):
        if not filters:
            search_query = {
                'query': {
                    'match': {
                        '_all': {
                            "query": query,
                            "operator": "and"
                        }
                    },
                }
            }
        else:
            search_query = {
                'query': {
                    'bool': {
                        'must': {
                            'match': {
                                '_all': {
                                    'query': query,
                                    'operator': 'and'
                                }
                            }
                        },
                        'filter': [
                            {'terms': {f'{k}_filter': v}} for k, v in filters.items()
                        ]
                    }
                }
            }

        result = self._search(search_query, content_types)

        def parse_result(hit):
            source = hit['_source']
            search_index = self.get_search_index(hit['_type'])
            if search_index:
                result_fields = [
                    field for field in search_index.get_result_fields() if field in source.keys()
                ]
                result = {field: source[field] for field in result_fields}
                result.update({
                    'id': hit['_id'],
                    'content_type': hit['_type']
                })
                return result

        return filter(lambda hit: hit is not None, map(parse_result, result['hits']['hits']))

    def autocomplete(self, query, content_types=None):
        autocomplete_query = {
            'autocomplete': {
                'prefix': query,
                'completion': {
                    'field': 'autocomplete',
                    'fuzzy': {
                        'fuzziness': 0
                    },
                    'size': 10,
                }
            }
        }

        if content_types:
            autocomplete_query['autocomplete']['completion']['contexts'] = {
                'content_type': content_types
            }

        result = self._suggest(autocomplete_query)

        def parse_result(hit):
            source = hit['_source']
            search_index = self.get_search_index(hit['_type'])
            if search_index:
                result_fields = [
                    field for field in search_index.get_autocomplete_result_fields()
                    if field in source.keys()
                ]
                result = {field: source[field] for field in result_fields}
                result.update({
                    'id': hit['_id'],
                    'content_type': hit['_type'],
                    'text': hit['text']
                })
                return result

        return filter(
            lambda hit: hit is not None, map(parse_result, result['autocomplete'][0]['options'])
        )
