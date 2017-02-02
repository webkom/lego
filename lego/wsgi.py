"""
WSGI config for lego project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os
import threading
from http.server import HTTPServer

import prometheus_client
from cassandra.cqlengine import connection
from cassandra.cqlengine.connection import cluster as cql_cluster
from cassandra.cqlengine.connection import session as cql_session
from django.core.wsgi import get_wsgi_application
from structlog import get_logger

from lego import settings

log = get_logger()

try:
    from uwsgidecorators import postfork
except ImportError:
    pass
else:
    import uwsgi

    @postfork
    def cassandra_init():
        """
        Initialize a new Cassandra session in the context.
        Ensures that a new session is returned for every new request.
        """

        log.info('cassandra_init')
        if cql_cluster is not None:
            cql_cluster.shutdown()
        if cql_session is not None:
            cql_session.shutdown()
        connection.setup(
            hosts=settings.STREAM_CASSANDRA_HOSTS,
            consistency=settings.STREAM_CASSANDRA_CONSISTENCY_LEVEL,
            default_keyspace=settings.STREAM_DEFAULT_KEYSPACE,
            **settings.CASSANDRA_DRIVER_KWARGS
        )

    @postfork
    def prometheus_init():
        """
        Starts a prometheus metrics server on PORT+WORKER_ID
        """

        class PrometheusEndpointServer(threading.Thread):
            """
            A thread class that holds an http and makes it serve_forever().
            """

            def __init__(self, httpd, *args, **kwargs):
                self.httpd = httpd
                super(PrometheusEndpointServer, self).__init__(*args, **kwargs)

            def run(self):
                self.httpd.serve_forever()

        log.info('prometheus_init')
        metrics_port = int(os.environ['PORT']) + uwsgi.worker_id()
        httpd = HTTPServer(('', metrics_port), prometheus_client.MetricsHandler)
        thread = PrometheusEndpointServer(httpd)
        thread.daemon = True
        thread.start()
        log.info('prometheus_listening', port=metrics_port)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lego.settings')

application = get_wsgi_application()
