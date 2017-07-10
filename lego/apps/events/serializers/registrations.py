from django.db import transaction
from rest_framework import serializers
from rest_framework_jwt.serializers import User

from lego.apps.events import constants
from lego.apps.events.fields import (ChargeStatusField, FeedbackField, PresenceField,
                                     SetChargeStatusField)
from lego.apps.events.models import Pool, Registration
from lego.apps.users.serializers.users import AdministrateUserSerializer, PublicUserSerializer
from lego.utils.fields import PrimaryKeyRelatedFieldNoPKOpt
from lego.utils.serializers import BasisModelSerializer


class AdminRegistrationCreateAndUpdateSerializer(serializers.Serializer):
    user = PrimaryKeyRelatedFieldNoPKOpt(queryset=User.objects.all())
    pool = PrimaryKeyRelatedFieldNoPKOpt(queryset=Pool.objects.all())
    feedback = serializers.CharField(required=False)
    admin_reason = serializers.CharField(required=True)


class RegistrationCreateAndUpdateSerializer(BasisModelSerializer):
    captcha_response = serializers.CharField(required=False)
    charge_status = SetChargeStatusField(
        required=False, choices=(constants.PAYMENT_MANUAL, constants.PAYMENT_FAILURE)
    )
    presence = PresenceField(required=False, choices=constants.PRESENCE_CHOICES)

    class Meta:
        model = Registration
        fields = ('id', 'feedback', 'presence', 'captcha_response', 'charge_status')

    def update(self, instance, validated_data):
        with transaction.atomic():
            presence = validated_data.pop('presence')
            super().update(instance, validated_data)
            instance.set_presence(presence)


class RegistrationReadSerializer(BasisModelSerializer):
    user = PublicUserSerializer()
    feedback = FeedbackField()

    class Meta:
        model = Registration
        fields = ('id', 'user', 'pool', 'feedback', 'status')
        read_only = True


class RegistrationPaymentReadSerializer(RegistrationReadSerializer):
    charge_status = ChargeStatusField()

    class Meta(RegistrationReadSerializer.Meta):
        fields = RegistrationReadSerializer.Meta.fields + ('charge_status', )


class RegistrationReadDetailedSerializer(BasisModelSerializer):
    user = AdministrateUserSerializer()

    class Meta:
        model = Registration
        fields = ('id', 'user', 'pool', 'event', 'presence', 'feedback', 'status',
                  'registration_date', 'unregistration_date', 'admin_reason',
                  'charge_id', 'charge_status', 'charge_amount', 'charge_amount_refunded')
        read_only = True


class StripeTokenSerializer(serializers.Serializer):
    token = serializers.CharField()


class StripeObjectSerializer(serializers.Serializer):
    id = serializers.CharField()
    amount = serializers.IntegerField()
    amount_refunded = serializers.IntegerField()
    status = serializers.CharField()
