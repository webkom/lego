from rest_framework import serializers

from lego.apps.events.serializers.events import EventReadDetailedSerializer
from lego.apps.events.serializers.registrations import (
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


class WebsocketSerializer(serializers.Serializer):
    type = serializers.CharField()
    meta = MetaSerializer()
    payload = serializers.DictField()


class RegistrationReadSocketSerializer(WebsocketSerializer):
    payload = RegistrationPublicReadSerializer()


class RegistrationPaymentReadSocketSerializer(WebsocketSerializer):
    payload = RegistrationPaymentReadSerializer()


class RegistrationPaymentInitiateSocketSerializer(
    RegistrationPaymentReadSocketSerializer
):
    meta = PaymentIntentMetaSerializer()


class EventReadDetailedSocketSerializer(WebsocketSerializer):
    payload = EventReadDetailedSerializer()
