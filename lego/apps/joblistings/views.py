from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets

from lego.apps.joblistings.filters import JoblistingFilterSet
from lego.apps.joblistings.models import Joblisting
from lego.apps.joblistings.serializer import (
    JoblistingCreateAndUpdateSerializer,
    JoblistingDetailedSerializer,
    JoblistingSerializer,
)
from lego.apps.permissions.api.views import AllowedPermissionsMixin


class JoblistingViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    filterset_class = JoblistingFilterSet
    ordering = "-created_at"

    def get_object(self) -> Joblisting:
        queryset = self.get_queryset()
        pk = self.kwargs.get("pk")

        try:
            obj = queryset.get(id=pk)
        except (Joblisting.DoesNotExist, ValueError):
            obj = get_object_or_404(queryset, slug=pk)

        try:
            self.check_object_permissions(self.request, obj)
        except PermissionError:
            raise Http404 from None

        if obj.visible_from > timezone.now() and self.request.user != obj.created_by:
            raise Http404 from None

        return obj

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return JoblistingCreateAndUpdateSerializer

        elif self.action in ["retrieve", "destroy"]:
            return JoblistingDetailedSerializer

        return JoblistingSerializer

    def get_queryset(self):
        queryset = Joblisting.objects.all()

        params = self.request.query_params

        # Disable pagination if filters are applied
        if params and any(
            params.get(key) for key in self.filterset_class.get_filters()
        ):
            self.pagination_class = None

        return queryset
