from django.conf import settings
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.response import Response

from lego.apps.events.tasks import stripe_webhook_event
from lego.apps.users.models import User


class StripeWebhookSerializer(serializers.Serializer):
    id = serializers.CharField()
    type = serializers.CharField()


class StripeAuthentication(BasicAuthentication):

    def authenticate_credentials(self, userid, password):
        if userid == settings.STRIPE_WEBHOOK_USERNAME \
                and password == settings.STRIPE_WEBHOOK_PASSWORD:
            return User(), None
        return None


class StripeWebhook(viewsets.GenericViewSet):
    authentication_classes = [StripeAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StripeWebhookSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event_id = serializer.data['id']
        event_type = serializer.data['type']
        stripe_webhook_event.delay(event_id=event_id, event_type=event_type)
        return Response(status=status.HTTP_200_OK)
