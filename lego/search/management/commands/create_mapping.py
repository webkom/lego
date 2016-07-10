from django.core.management import BaseCommand

from lego.search.backends.elasticsearch import backend as elasticsearch_backend


class Command(BaseCommand):
    help = 'Upload the index-template to Elasticsearch.'

    def handle(self, *args, **options):
        elasticsearch_backend._create_template()
