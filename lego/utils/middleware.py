import re
import timeit
from os import environ
from uuid import uuid4

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from structlog import get_logger

from lego.apps.files.validators import KEY_REGEX_RAW
from lego.apps.stats.statsd_client import statsd

log = get_logger()
development = getattr(settings, 'DEVELOPMENT', False)


def method(request):
    method = request.method
    if method not in (
            'GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'TRACE', 'OPTIONS', 'CONNECT', 'PATCH'
    ):
        return 'INVALID'
    return method


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
            context['current_user'] = request.user.id
        else:
            context['current_user'] = None

        context['version'] = environ.get('RELEASE', 'latest')
        context['system'] = 'lego'
        context['environment'] = \
            'development' if development else getattr(settings, 'ENVIRONMENT_NAME', 'unknown')
        context['request_path'] = request.path
        context['request_method'] = request.method

        request.log = log.new(**context)


class StatsDBeforeMiddleware(MiddlewareMixin):

    def process_request(self, request):
        statsd.incr(f'request.total.{method(request)}')
        request.statsd_before_middleware_event = timeit.default_timer()

    def process_response(self, request, response):
        statsd.incr(f'response.total.{method(request)}')

        if hasattr(request, 'statsd_before_middleware_event'):
            statsd.timing(
                f'request.latency.{method(request)}',
                timeit.default_timer() - request.statsd_before_middleware_event
            )
        else:
            statsd.incr(f'request.unknown_latency.{method(request)}')

        return response


class StatsDAfterMiddleware(MiddlewareMixin):

    def process_request(self, request):
        request.statsd_after_middleware_event = timeit.default_timer()

    def process_response(self, request, response):
        if hasattr(request, 'statsd_after_middleware_event'):
            statsd.timing(
                f'response.latency.{method(request)}',
                timeit.default_timer() - request.statsd_after_middleware_event
            )
        else:
            statsd.incr(f'response.unknown_latency.{method(request)}')

        return response


class CORSPatchMiddleware(MiddlewareMixin):
    """
    The cors header seems to break the file upload endpoint when using firefox.
    This is a temporarily patch to fix this.
    """

    header = 'Access-Control-Allow-Origin'
    regex_path = f'/api/v1/files/{KEY_REGEX_RAW}/upload_success/'
    regex = re.compile(regex_path)

    def process_response(self, request, response):
        if self.regex.match(request.path):
            response[self.header] = '*'
        return response
