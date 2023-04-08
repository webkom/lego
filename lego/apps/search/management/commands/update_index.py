import logging

from lego.apps.search import backend
from lego.apps.search.registry import index_registry
from lego.utils.management_command import BaseCommand

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Update all search indexes."

    def run(self, *args, **options):
        log.info("Updating indexes")
        search_backend = backend.current_backend
        log.info(f"Using the {search_backend.name} backend...")
        for content_type, index in index_registry.items():
            log.info(f"Updating the {content_type} index")
            index.update()
        log.info("Done!")
