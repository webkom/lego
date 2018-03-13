import atexit
import multiprocessing
import socket
import threading
from threading import Thread
from time import sleep
from urllib.error import URLError

import prometheus_client
from django.conf import settings
from structlog import get_logger

log = get_logger(app='utils')

pusher = None


class MetricsPusher(Thread):
    def __init__(self, pushgateway, job, grouping_key):
        self.pushgateway = pushgateway
        self.job = job
        self.grouping_key = grouping_key
        super().__init__()
        self.daemon = True
        self.running = True

    def pause(self):
        self.running = False

    def run(self):
        log.info('starting_metrics_pusher')
        self.grouping_key['process'] = multiprocessing.current_process().pid
        self.grouping_key['thread'] = threading.current_thread().name

        while self.running:
            try:
                prometheus_client.pushadd_to_gateway(
                    self.pushgateway, job=self.job, registry=prometheus_client.REGISTRY,
                    grouping_key=self.grouping_key
                )
            except (ConnectionError, URLError):
                log.error('metrics_pusher_failed')
            sleep(20)
        log.info('stopped_metrics_pusher')


class MetricsExporter:
    def __init__(self):
        pushgateway = getattr(settings, 'PUSHGATEWAY', None)
        if not pushgateway:
            log.info('no_pushgateway_url')
            return

        self.pusher = MetricsPusher(
            pushgateway, 'lego',
            {
                'instance': socket.gethostname(),
                'environment': settings.ENVIRONMENT_NAME
            }
        )

        atexit.register(self.join)
        self.pusher.start()

    def join(self):
        self.pusher.pause()
        try:
            self.pusher.join()
        except RuntimeError:
            # consumer thread has not started
            pass


def setup_pusher():
    global pusher

    if not pusher:
        log.info('setting_up_pusher')
        pusher = MetricsExporter()
