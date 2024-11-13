from rest_framework import mixins, permissions, viewsets
from rest_framework.response import Response

from lego.apps.users.models import User
from lego.apps.users.serializers.users import PublicUserWithGroupsSerializer


class LeaderBoardViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = PublicUserWithGroupsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            User.objects.filter(achievements__isnull=False)
            .order_by("-achievements_score")
            .distinct()[:50]
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
