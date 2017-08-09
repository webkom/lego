from rest_framework import mixins, viewsets

from lego.apps.email.models import EmailAddress, EmailList
from lego.apps.email.serializers import EmailAddressSerializer, EmailListSerializer


class EmailListViewSet(mixins.CreateModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    serializer_class = EmailListSerializer
    queryset = EmailList.objects.all()
    ordering = 'id'


class EmailViewSet(viewsets.ModelViewSet):
    serializer_class = EmailAddressSerializer
    queryset = EmailAddress.objects.all()

    pagination_class = None
