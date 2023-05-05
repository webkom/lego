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
    pagination_class = None
    filterset_class = JoblistingFilterSet
    ordering = "-created_at"

    def get_object(self) -> Joblisting:
        queryset = self.get_queryset()
        pk = self.kwargs.get("pk")

        try:
            obj = queryset.get(id=pk)
        except Joblisting.DoesNotExist:
            obj = get_object_or_404(queryset, slug=pk)

        try:
            self.check_object_permissions(self.request, obj)
        except PermissionError:
            raise Http404
        return obj

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return JoblistingCreateAndUpdateSerializer

        elif self.action in ["retrieve", "destroy"]:
            return JoblistingDetailedSerializer

        return JoblistingSerializer

    def get_queryset(self):
        if self.action == "list":
            return Joblisting.objects.filter(
                visible_from__lte=timezone.now(), visible_to__gte=timezone.now()
            )
        return Joblisting.objects.all()
