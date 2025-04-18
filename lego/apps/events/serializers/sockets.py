from rest_framework import serializers

from lego.apps.events.serializers.events import EventReadDetailedSerializer
from lego.apps.events.serializers.registrations import (
    RegistrationAnonymizedReadSerializer,
    RegistrationPaymentReadSerializer,
    RegistrationPublicReadSerializer,
)
from lego.apps.feeds.serializers.sockets import WebsocketSerializer


class MetaSerializer(serializers.Serializer):
    event_id = serializers.IntegerField(required=False)
    activation_time = serializers.DateTimeField(required=False)
    from_pool = serializers.IntegerField(required=False)
    error_message = serializers.CharField(required=False)
    success_message = serializers.CharField(required=False)


class PaymentIntentMetaSerializer(MetaSerializer):
    client_secret = serializers.CharField(required=True)


class PaymentErrorSerialzer(MetaSerializer):
    payment_error = serializers.CharField(required=True)


class EventWebsocketSerializer(WebsocketSerializer):
    meta = MetaSerializer()


class RegistrationReadSocketSerializer(EventWebsocketSerializer):
    payload = RegistrationPublicReadSerializer()  # type: ignore


class RegistrationReadAnonymizedSocketSerializer(EventWebsocketSerializer):
    payload = RegistrationAnonymizedReadSerializer()  # type: ignore


class RegistrationPaymentReadSocketSerializer(EventWebsocketSerializer):
    payload = RegistrationPaymentReadSerializer()  # type: ignore


class RegistrationPaymentReadErrorSerializer(RegistrationPaymentReadSocketSerializer):
    meta = PaymentErrorSerialzer()


class RegistrationPaymentInitiateSocketSerializer(
    RegistrationPaymentReadSocketSerializer
):
    meta = PaymentIntentMetaSerializer()


class EventReadDetailedSocketSerializer(EventWebsocketSerializer):
    payload = EventReadDetailedSerializer()  # type: ignore
