from django.utils.deprecation import MiddlewareMixin
from structlog import get_logger

log = get_logger()


class LoggingMiddleware(MiddlewareMixin):
    """
    Attach request information to the log context
    Supports:
    * current_user
    * request_id
    """

    def process_request(self, request):
        context = {}

        request_id = request.META.get('HTTP_REQUEST_ID')
        if request_id:
            context['request_id'] = request_id

        if request.user.is_authenticated():
            context['current_user'] = request.user.username
        else:
            context['current_user'] = None

        request.log = log.new(**context)
