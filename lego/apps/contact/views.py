from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from .send import send_message
from .serializers import ContactFormSerializer


class ContactFormViewSet(viewsets.GenericViewSet):

    permission_classes = (permissions.AllowAny,)
    serializer_class = ContactFormSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        title = serializer.validated_data["title"]
        message = serializer.validated_data["message"]
        anonymous = serializer.validated_data["anonymous"]
        recipient_group = serializer.validated_data["recipient_group"]

        send_message(title, message, request.user, anonymous, recipient_group)

        if recipient_group:
            serializer.validated_data["recipient_group"] = recipient_group.id

        return Response(serializer.validated_data, status=status.HTTP_202_ACCEPTED)
