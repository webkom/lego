from rest_framework.response import Response
from rest_framework.views import APIView
from structlog import get_logger

from .permissions import HealthPermission

log = get_logger()


class HealthView(APIView):

    permission_classes = [HealthPermission]

    def get(self, request):
        return Response({})
