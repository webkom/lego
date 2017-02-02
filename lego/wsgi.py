import os

from cassandra.cqlengine import connection
from cassandra.cqlengine.connection import cluster as cql_cluster
from cassandra.cqlengine.connection import session as cql_session
from django.core.wsgi import get_wsgi_application

from lego import settings

try:
    from uwsgidecorators import postfork
except ImportError:
    print('Lego is not running under a uwsgi context')
else:
    @postfork
    def cassandra_init():
        """
        Initialize a new Cassandra session in the context.
        Ensures that a new session is returned for every new request.
        """

        print('Initializing cassandra session')
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


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lego.settings')

application = get_wsgi_application()
