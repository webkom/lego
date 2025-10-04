from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from lego.apps.user_commands.models import UserCommand
from lego.apps.user_commands.serializer import UserCommandSerializer


class UserCommandViewSet(viewsets.ModelViewSet):
    queryset = UserCommand.objects.all()
    serializer_class = UserCommandSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    @action(detail=False, methods=["post"])
    def record_usage(self, request):
        command_id = request.data.get("command_id")
        if not command_id:
            return Response(
                {"error": "Missing command_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cmd = UserCommand.objects.record_usage(request.user, command_id)
        return Response(UserCommandSerializer(cmd).data)

    @action(detail=False, methods=["get"])
    def suggestions(self, request):
        qs = self.get_queryset().order_by("position")[:5]
        visible, buffer = qs[:3], qs[3:]
        return Response(
            {
                "visible": UserCommandSerializer(visible, many=True).data,
                "buffer": UserCommandSerializer(buffer, many=True).data,
            }
        )
