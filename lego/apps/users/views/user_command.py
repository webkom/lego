from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from lego.apps.users.validators import validate_command_id


class UserCommandViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"])
    def use(self, request):
        command_id = request.data.get("command_id")

        if not command_id:
            return Response(
                {"error": "Missing command_id"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            validate_command_id(command_id)
        except Exception:
            return Response(
                {"error": "Invalid command_id"}, status=status.HTTP_400_BAD_REQUEST
            )

        cmds = request.user.record_command_usage(command_id)
        return Response({"recent_commands": cmds})

    @action(detail=False, methods=["get"])
    def suggestions(self, request):
        return Response(request.user.get_command_suggestions())
