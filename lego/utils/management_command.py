import logging

from django.core.management import BaseCommand as DjangoBaseCommand


class BaseCommand(DjangoBaseCommand):
    """
    Base command for our management commands. Implement the .run() function.
    """

    def handle(self, *args, **options):
        """
        Set log level based on builtin -v or --verbose flag.
        -v 0 CRITICAL
        -v 1 INFO
        -v 2 DEBUG
        """
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
