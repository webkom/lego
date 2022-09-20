import ast
from random import choice

from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.permissions.constants import EDIT
from lego.apps.quotes.filters import QuotesFilterSet
from lego.apps.quotes.models import Quote
from lego.apps.quotes.serializers import QuoteCreateAndUpdateSerializer, QuoteSerializer


class QuoteViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):

    queryset = Quote.objects.all().prefetch_related("tags")
    filterset_class = QuotesFilterSet
    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ["reaction_count"]
    ordering = "-created_at"

    def get_queryset(self):
        if self.request is None:
            return Quote.objects.none()
        access_unapproved = self.request.user.has_perm(EDIT, self.queryset)

        queryset = self.queryset.annotate(reaction_count=Count("reactions"))

        if not access_unapproved:
            return queryset.filter(approved=True)
        return queryset

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return QuoteCreateAndUpdateSerializer
        return QuoteSerializer

    @action(detail=True, methods=["PUT"])
    def approve(self, *args, **kwargs):
        instance = self.get_object()
        if instance.created_by == self.request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        instance.approve()
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["PUT"])
    def unapprove(self, *args, **kwargs):
        instance = self.get_object()
        instance.unapprove()
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def random(self, request):
        seen_query_param = request.query_params.get("seen", "[]")
        seen = ast.literal_eval(seen_query_param)
        queryset = self.get_queryset().filter(approved=True)
        # Check if there are more "fresh", ie unseen, quotes. Otherwise,
        # we have no choice but to show a stale one.
        if len(seen) < len(queryset):
            queryset = queryset.exclude(pk__in=seen)
        values = queryset.values_list("pk", flat=True)
        if not values:
            return Response(status=status.HTTP_204_NO_CONTENT)

        instance = queryset.get(pk=choice(values))
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
