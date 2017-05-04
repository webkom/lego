from rest_framework import viewsets

from lego.apps.email.models import EmailList, EmailAddress
from lego.apps.email.serializers import EmailListSerializer, EmailAddressSerializer


class EmailListViewSet(viewsets.ModelViewSet):
    serializer_class = EmailListSerializer
    queryset = EmailList.objects.all()

    pagination_class = None


class EmailViewSet(viewsets.ModelViewSet):
    serializer_class = EmailAddressSerializer
    queryset = EmailAddress.objects.all()

    pagination_class = None