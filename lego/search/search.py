from lego.search.es import backend as elasticsearch_backend


def autocomplete(query):
    result = elasticsearch_backend.autocomplete(query)
    return result


def search(query):
    result = elasticsearch_backend.search(query)
    return result
