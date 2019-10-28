from random import choice

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.permissions.constants import EDIT
from lego.apps.quotes.filters import QuotesFilterSet
from lego.apps.quotes.models import Quote
from lego.apps.quotes.serializers import QuoteCreateAndUpdateSerializer, QuoteSerializer


class QuoteViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):

    queryset = Quote.objects.all().prefetch_related("tags")
    filter_class = QuotesFilterSet
    ordering = "-created_at"

    def get_queryset(self):
        access_unapproved = self.request.user.has_perm(EDIT, self.queryset)

        if not access_unapproved:
            return self.queryset.filter(approved=True)
        return self.queryset

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return QuoteCreateAndUpdateSerializer
        return QuoteSerializer

    @action(detail=True, methods=["PUT"])
    def approve(self, *args, **kwargs):
        instance = self.get_object()
        instance.approve()
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["PUT"])
    def unapprove(self, *args, **kwargs):
        instance = self.get_object()
        instance.unapprove()
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def random(self, request):
        seen = [3, 12]
        queryset = self.get_queryset().filter(approved=True)
        if len(seen) != len(queryset):
            queryset = queryset.exclude(pk__in=seen)
        values = queryset.values_list("pk", flat=True)
        if not values:
            return Response(status=status.HTTP_204_NO_CONTENT)

        instance = queryset.get(pk=choice(values))
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
