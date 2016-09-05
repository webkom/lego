from django.core.management import BaseCommand

from lego.apps.search.backends.elasticsearch import backend as elasticsearch_backend
from lego.apps.search.registry import index_registry


class Command(BaseCommand):
    help = 'Rebuild all indexes in Elasticsearch.'

    def handle(self, *args, **options):
        elasticsearch_backend.clear()
        for index in index_registry.values():
            index.update()
