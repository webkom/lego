from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from lego.apps.user_commands.models import UserCommand
from lego.apps.user_commands.serializer import UserCommandSerializer


class UserCommandViewSet(viewsets.ModelViewSet):
    serializer_class = UserCommandSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserCommand.objects.filter(user=self.request.user)

    @action(detail=False, methods=["post"])
    def set_pins(self, request):
        """
        Set/reorder pinned commands.
        Example payload:
        { "pins": ["cmd1", "cmd2", "cmd3"] }
        """
        pins = request.data.get("pins", [])

        if len(pins) > 5:
            return Response(
                {"error": "You can pin at most 5 commands."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Reset old pins
        UserCommand.objects.filter(user=request.user).update(pinned_position=None)

        # Apply new positions
        for idx, cmd_id in enumerate(pins, start=1):
            obj, _ = UserCommand.objects.get_or_create(
                user=request.user, command_id=cmd_id
            )
            obj.pinned_position = idx
            obj.save(update_fields=["pinned_position"])

        return Response({"status": "ok"})

    @action(detail=False, methods=["post"])
    def bulk_records(self, request):
        updates = request.data.get("updates", {})
        for cmd_id, count in updates.item():
            obj, _ = UserCommand.objects.get_or_create(
                user=request.user, command_id=cmd_id
            )
            obj.usage_count += int(count)
            obj.save(update_fields=["usage_count", "last_used"])
        return Response({"status": "ok"})

    @action(detail=False, methods=["get"])
    def suggestions(self, request):
        qs = self.get_queryset()
        pinned = qs.filter(pinned_position__isnull=False).order_by("pinned_position")
        suggested = qs.exclude(pinned_position__isnull=False).order_by("-usage_count")[
            :5
        ]
        return Response(
            {
                "pinned": UserCommandSerializer(pinned, many=True).data,
                "suggested": UserCommandSerializer(suggested, many=True).data,
            }
        )
