from rest_framework import viewsets

from lego.apps.permissions.tests.models import TestModel
from lego.apps.permissions.tests.serializer import TestSerializer


class TestViewSet(viewsets.ModelViewSet):
    queryset = TestModel.objects.all()
    serializer_class = TestSerializer
