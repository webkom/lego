import logging
import signal
import sys

from django.core.management import BaseCommand as DjangoBaseCommand

log = logging.getLogger(__name__)


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

        try:
            # Gracefully exit on sigterm.
            signal.signal(signal.SIGTERM, self._handle_sigterm)

            # A SIGUSR1 signals an exit with an autorestart
            signal.signal(signal.SIGUSR1, self._handle_sigusr1)

            # Handle Keyboard Interrupt
            signal.signal(signal.SIGINT, self._handle_sigterm)

            return self.run(*args, **options)

        except Exception:
            log.exception('Fatal exception, exiting...')
            sys.exit(1)

    def _handle_sigterm(self, signum, frame):
        self.close()
        sys.exit(0)

    def _handle_sigusr1(self, signum, frame):
        self._handle_sigterm(signum, frame)

    def run(self, *args, **options):
        raise NotImplementedError('Please implement the .run method')

    def close(self):
        pass
