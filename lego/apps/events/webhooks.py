from django.conf import settings
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.response import Response
from stripe import SignatureVerificationError
from stripe.webhook import WebhookSignature

from lego.apps.events.tasks import stripe_webhook_event


class StripeWebhookSerializer(serializers.Serializer):
    id = serializers.CharField()
    type = serializers.CharField()


class StripeWebhookPermission(permissions.BasePermission):
    """
    Check the HTTP_STRIPE_SIGNATURE header and grant access to valid requests.
    """

    def has_permission(self, request, view):
        secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)
        request_header = request.META.get('HTTP_STRIPE_SIGNATURE')

        if not (secret and request_header):
            return False

        try:
            WebhookSignature.verify_header(request.data, request_header, secret, 300)
        except SignatureVerificationError:
            return False

        return True


class StripeWebhook(viewsets.GenericViewSet):
    authentication_classes = []
    permission_classes = [StripeWebhookPermission]
    serializer_class = StripeWebhookSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event_id = serializer.data['id']
        event_type = serializer.data['type']
        stripe_webhook_event.delay(event_id=event_id, event_type=event_type)
        return Response(status=status.HTTP_200_OK)
