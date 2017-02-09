from rest_framework import viewsets, renderers
from rest_framework.response import Response

from .permissions import ICalTokenPermission


class ICalViewset(viewsets.ViewSet):

    permission_classes = (ICalTokenPermission, )
    authentication_classes = ()
    renderer_classes = (renderers.BaseRenderer)

    def list(self, request):
        return Response({})

