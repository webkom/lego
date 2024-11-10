from rest_framework import permissions, mixins, viewsets
from rest_framework.response import Response

from lego.apps.users.serializers.users import PublicUserWithGroupsSerializer
from lego.apps.users.models import User


class LeaderBoardViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = PublicUserWithGroupsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(achievements__isnull=False).distinct()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        sorted_data = sorted(
            serializer.data, key=lambda x: x["achievement_score"], reverse=True
        )[:50]

        return Response(sorted_data)