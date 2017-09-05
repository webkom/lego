from django.db.utils import IntegrityError
from rest_framework import status
from rest_framework.compat import set_rollback
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler
from structlog import get_logger

log = get_logger()


def exception_handler(exc, context):
    """
    Return special responses on exceptions not supported by drf.
    """
    response = drf_exception_handler(exc, context)

    # Check for IntegrityError, use a custom status code for this.
    if not response and isinstance(exc, IntegrityError):
        set_rollback()
        response = Response(
            {'detail': 'Some values are supposed to be unique but are not.'},
            status=status.HTTP_409_CONFLICT
        )

    if response:
        detail = None
        if isinstance(response.data, dict):
            detail = response.data.get('detail')

        log.warn(
            'request_error',
            status_code=response.status_code,
            detail=detail
        )
    else:
        log.error('unhandled_request_exception', exc=exc)

    return response
