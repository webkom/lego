import timeit
from os import environ
from uuid import uuid4

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from structlog import get_logger

from lego.apps.stats.statsd_client import statsd

log = get_logger()
development = getattr(settings, 'DEVELOPMENT', False)


class LoggingMiddleware(MiddlewareMixin):
    """
    Attach request information to the log context
    Supports:
    * current_user
    * request_id
    """

    def generate_request_id(self):
        return str(uuid4())

    def process_request(self, request):
        context = {}

        request_id = request.META.get('HTTP_REQUEST_ID')
        if request_id:
            context['request_id'] = request_id
        else:
            context['request_id'] = self.generate_request_id()

        if request.user.is_authenticated():
            context['current_user'] = request.user.username
        else:
            context['current_user'] = None

        context['version'] = environ.get('RELEASE', 'latest')
        context['system'] = 'lego'
        context['environment'] = 'development' if development else 'production'
        context['request_path'] = request.path
        context['request_method'] = request.method

        request.log = log.new(**context)


class StatsDBeforeMiddleware(MiddlewareMixin):

    def process_request(self, request):
        statsd.incr('requests.total')
        request.statsd_before_middleware_event = timeit.default_timer()

    def process_response(self, request, response):
        statsd.incr('responses.total')

        if hasattr(request, 'statsd_before_middleware_event'):
            statsd.timing(
                'request.latency', timeit.default_timer() - request.statsd_before_middleware_event
            )
        else:
            statsd.incr('requests.unknown_latency')

        return response


class StatsDAfterMiddleware(MiddlewareMixin):

    def method(self, request):
        method = request.method
        if method not in (
                'GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'TRACE', 'OPTIONS', 'CONNECT', 'PATCH'
        ):
            return 'INVALID'
        return method

    def process_request(self, request):
        request.statsd_after_middleware_event = timeit.default_timer()

    def process_response(self, request, response):
        if hasattr(request, 'statsd_after_middleware_event'):
            statsd.timing(
                'response.latency', timeit.default_timer() - request.statsd_after_middleware_event
            )
        else:
            statsd.incr('response.unknown_latency')

        method = self.method(request)
        statsd.incr(f'request.method.{method}')

        return response
