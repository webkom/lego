import certifi
from django.conf import settings
from django.template.loader import render_to_string
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


class ElasticSearchBackend:

    def __init__(self):
        self.connection = Elasticsearch(hosts=settings.ELASTICSEARCH, ca_certs=certifi.where())

    def _bulk(self, actions):
        """
        Execute many actions using the bulk interface.
        """
        return bulk(self.connection, actions, stats_only=True)

    def _index(self, payload, type, id):
        action = {
            '_op_type': 'index',
            '_index': settings.SEARCH_INDEX,
            '_type': type,
            '_id': id,
        }
        action.update(payload)
        return action

    def _remove(self, type, id):
        action = {
            '_op_type': 'delete',
            '_index': settings.SEARCH_INDEX,
            '_type': type,
            '_id': id,
        }
        return action

    def _clear(self):
        return self.connection.indices.delete(settings.SEARCH_INDEX)

    def _search(self, payload):
        return self.connection.search(settings.SEARCH_INDEX, body=payload)

    def _suggest(self, payload):
        return self.connection.suggest(payload, index=settings.SEARCH_INDEX)

    def _create_template(self, name=settings.SEARCH_TEMPLATE_NAME):
        context = {
            'index': settings.SEARCH_INDEX
        }
        template = render_to_string('search/templates/search_template.json', context)
        return self.connection.indices.put_template(name, template)

    def update_many(self, payload_tuples):
        return self._bulk([self._index(data, type, id) for data, type, id in payload_tuples])

    def remove_many(self, payload_tuples):
        return self._bulk([self._remove(type, id) for type, id in payload_tuples])

    def update(self, data, type, id):
        return self.update_many([(data, type, id)])

    def remove(self, type, id):
        return self.remove_many([(type, id)])

    def clear(self):
        self._clear()

    def autocomplete(self, query):
        autocomplete_query = {
            'autocomplete': {
                'text': query,
                'completion': {
                    'field': 'autocomplete',
                    'fuzzy': {
                        'fuzziness': 2
                    }
                }
            }
        }
        result = self._suggest(autocomplete_query)
        payload = result['autocomplete'][0]['options']
        if payload:
            return {
                'text': payload[0]['text'],
                'content_type': payload[0]['payload']['ct'],
                'object_id': payload[0]['payload']['id'],
            }
        return None

    def search(self, query):
        search_query = {
            'query': {
                'query_string': {
                    'query': query,
                    'analyze_wildcard': True,
                }
            }
        }
        payload = self._search(search_query)
        if payload:
            hits = payload['hits']['hits']
            return [{
                'content_type': hit['_source'][settings.SEARCH_DJANGO_CT_FIELD],
                'object_id': hit['_source'][settings.SEARCH_DJANGO_ID_FIELD]
            } for hit in hits]
        return None

backend = ElasticSearchBackend()
