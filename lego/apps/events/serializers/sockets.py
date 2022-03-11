from rest_framework import serializers

from lego.apps.events.serializers.events import EventReadDetailedSerializer
from lego.apps.events.serializers.registrations import (
    RegistrationAnonymizedReadSerializer,
    RegistrationPaymentReadSerializer,
    RegistrationPublicReadSerializer,
)


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


class WebsocketSerializer(serializers.Serializer):
    type = serializers.CharField()
    meta = MetaSerializer()
    payload = serializers.DictField()


class RegistrationReadSocketSerializer(WebsocketSerializer):
    payload = RegistrationPublicReadSerializer()  # type: ignore


class RegistrationReadAnonymizedSocketSerializer(WebsocketSerializer):
    payload = RegistrationAnonymizedReadSerializer()  # type: ignore


class RegistrationPaymentReadSocketSerializer(WebsocketSerializer):
    payload = RegistrationPaymentReadSerializer()  # type: ignore


class RegistrationPaymentReadErrorSerializer(RegistrationPaymentReadSocketSerializer):
    meta = PaymentErrorSerialzer()


class RegistrationPaymentInitiateSocketSerializer(
    RegistrationPaymentReadSocketSerializer
):
    meta = PaymentIntentMetaSerializer()


class EventReadDetailedSocketSerializer(WebsocketSerializer):
    payload = EventReadDetailedSerializer()  # type: ignore
