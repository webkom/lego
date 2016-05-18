from django.core.management import BaseCommand

from lego.search.es import backend as elasticsearch_backend
from lego.search.registry import index_registry


class Command(BaseCommand):
    help = "Rebuild all indexes in Elasticsearch."

    def handle(self, *args, **options):
        elasticsearch_backend.clear()
        for index in index_registry.values():
            index.update()
