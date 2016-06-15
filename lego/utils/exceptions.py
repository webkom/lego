from django.db.utils import IntegrityError
from raven.contrib.django.raven_compat.models import client
from rest_framework import status
from rest_framework.compat import set_rollback
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


def exception_handler(exc, context):
    """
    Return special responses on exceptions not supported by drf.
    """
    drf_handler = drf_exception_handler(exc, context)

    if drf_handler:
        return drf_handler

    # Check for IntegrityError, use a custom status code for this.
    if isinstance(exc, IntegrityError):
        client.captureException(exc)
        set_rollback()
        return Response({'detail': 'Some values are supposed to be unique but are not.'},
                        status=status.HTTP_409_CONFLICT)

    return None
