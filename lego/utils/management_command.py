from django.core.management import BaseCommand as DjangoBaseCommand
import logging


class BaseCommand(DjangoBaseCommand):

    def handle(self, *args, **options):
        verbosity = options['verbosity']
        log_levels = {
            0: logging.CRITICAL,
            1: logging.INFO,
            2: logging.DEBUG,
            3: logging.DEBUG
        }

        root_log = logging.getLogger('')
        for handler in root_log.handlers:
            handler.setLevel(log_levels[verbosity])

        return self.run(*args, **options)

    def run(self, *args, **options):
        raise NotImplementedError('Please implement the .run method')
