from django.core.management import BaseCommand

from lego.search.registry import index_registry


class Command(BaseCommand):
    help = "Update all indexes in Elasticsearch."

    def handle(self, *args, **options):
        for index in index_registry.values():
            index.update()
