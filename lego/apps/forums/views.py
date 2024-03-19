import os

from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.exceptions import NotAuthenticated, PermissionDenied

from lego import settings
from lego.apps.forums.models import Forum, Thread
from lego.apps.forums.serializers import (
    DetailedAdminForumSerializer,
    DetailedAdminThreadSerializer,
    DetailedForumSerializer,
    DetailedThreadSerializer,
    PublicForumSerializer,
    PublicThreadSerializer,
)
from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.permissions.constants import OBJECT_PERMISSIONS_FIELDS


class ForumsViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = Forum.objects.all()
    ordering = "-created_at"
    serializer_class = DetailedForumSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return PublicForumSerializer
        if self.request and self.request.user.is_authenticated:
            return DetailedAdminForumSerializer
        return super().get_serializer_class()

    def get_object(self) -> Forum:
        queryset = self.get_queryset()
        pk = self.kwargs.get("pk")

        try:
            obj = queryset.get(id=pk)
        except (TypeError, OverflowError, Forum.DoesNotExist, ValueError):
            obj = get_object_or_404(queryset, slug=pk)

        try:
            self.check_object_permissions(self.request, obj)
        except NotAuthenticated as e:
            raise Http404 from e
        except PermissionDenied as e:
            raise PermissionDenied from e
        return obj


class ThreadViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = Thread.objects.all()
    ordering = "-created_at"
    serializer_class = DetailedThreadSerializer

    def get_queryset(self):
        queryset = super().get_queryset().select_related("created_by")
        forum_id = self.kwargs.get("forum_id", None)
        if forum_id:
            queryset = queryset.filter(forum_id=forum_id)

        if self.action == "list":
            return queryset

        return queryset.prefetch_related(
            "comments", "comments__created_by", *OBJECT_PERMISSIONS_FIELDS
        )

    def get_serializer_class(self):
        if self.action == "list":
            return PublicThreadSerializer
        if self.request and self.request.user.is_authenticated:
            return DetailedAdminThreadSerializer

        return super().get_serializer_class()

    def get_object(self) -> Thread:
        queryset = self.get_queryset()
        pk = self.kwargs.get("pk")

        try:
            obj = queryset.get(id=pk)
        except (TypeError, OverflowError, Thread.DoesNotExist, ValueError):
            obj = get_object_or_404(queryset, slug=pk)

        try:
            self.check_object_permissions(self.request, obj)
        except NotAuthenticated as e:
            raise Http404 from e
        except PermissionDenied as e:
            raise PermissionDenied from e
        return obj


@csrf_exempt
def easter(request):
    if request.method == "DELETE":
        image_path = os.path.join(
            settings.BASE_DIR, "assets", "img", "c8a9356a064b183b.png"
        )
        try:
            with open(image_path, "rb") as image:
                return HttpResponse(image.read(), content_type="image/jpeg", status=418)
        except Exception:
            return HttpResponse(status=420)
    return HttpResponse(
        "Easter dawn whispers renewal, where hidden eggs and hopes bloom anew.",
        status=425,
    )
