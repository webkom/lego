from django.db.models import Count
from rest_framework import decorators, permissions, viewsets
from rest_framework.response import Response

from lego.apps.tags.models import Tag
from lego.apps.tags.serializers import TagDetailSerializer, TagListSerializer


class TagViewSet(
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):

    queryset = Tag.objects.all()
    ordering = "tag"
    serializer_class = TagListSerializer
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action != "list":
            return TagDetailSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.action in ["popular", "list"]:
            # Usage count
            related_fields = [
                related.name for related in queryset.model._meta.related_objects
            ]
            annotation = Count(related_fields[0])
            for related in related_fields[1:]:
                annotation += Count(related)
            return queryset.annotate(usages=annotation)

        if self.action == "retrieve":
            # Usage count and relation counts
            related_fields = [
                related.name for related in queryset.model._meta.related_objects
            ]
            annotation = Count(related_fields[0])
            for related in related_fields[1:]:
                annotation += Count(related)
            annotations = {f"{field}_count": Count(field) for field in related_fields}
            return queryset.annotate(usages=annotation, **annotations)

        return queryset

    @decorators.list_route(methods=["GET"])
    def popular(self, request):
        return Response(
            list(self.get_queryset().order_by("-usages").values("tag", "usages")[:15])
        )
