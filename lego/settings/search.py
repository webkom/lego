HAYSTACK_DEFAULT_OPERATOR = 'AND'
HAYSTACK_DOCUMENT_FIELD = 'search_text'
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 20
HAYSTACK_ITERATOR_LOAD_PER_QUERY = 20
HAYSTACK_DJANGO_CT_FIELD = 'lego_type'
HAYSTACK_DJANGO_ID_FIELD = 'lego_id'
HAYSTACK_SIGNAL_PROCESSOR = 'celery_haystack.signals.CelerySignalProcessor'

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'lego_search',
    },
}
