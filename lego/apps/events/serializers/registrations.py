from django.db import transaction
from rest_framework import serializers

from rest_framework_jwt.serializers import User

from lego.apps.events import constants
from lego.apps.events.fields import (
    ConsentField,
    PersonalChargeStatusField,
    PersonalConsentField,
    PersonalFeedbackField,
    PersonalPresenceField,
    PresenceField,
    SetChargeStatusField,
)
from lego.apps.events.models import Pool, Registration
from lego.apps.users.serializers.users import (
    AdministrateUserSerializer,
    PublicUserSerializer,
)
from lego.utils.fields import PrimaryKeyRelatedFieldNoPKOpt
from lego.utils.serializers import BasisModelSerializer


class AdminUnregisterSerializer(serializers.Serializer):
    user = PrimaryKeyRelatedFieldNoPKOpt(queryset=User.objects.all())
    admin_unregistration_reason = serializers.CharField(required=True)


class AdminRegistrationCreateAndUpdateSerializer(serializers.Serializer):
    user = PrimaryKeyRelatedFieldNoPKOpt(queryset=User.objects.all())
    pool = PrimaryKeyRelatedFieldNoPKOpt(queryset=Pool.objects.all(), required=False)
    feedback = serializers.CharField(
        required=False, max_length=Registration._meta.get_field("feedback").max_length
    )
    admin_registration_reason = serializers.CharField(
        required=True,
        max_length=Registration._meta.get_field("admin_registration_reason").max_length,
    )


class RegistrationCreateAndUpdateSerializer(BasisModelSerializer):
    captcha_response = serializers.CharField(required=False)
    charge_status = SetChargeStatusField(
        required=False, choices=(constants.PAYMENT_MANUAL, constants.PAYMENT_FAILURE)
    )
    presence = PresenceField(required=False, choices=constants.PRESENCE_CHOICES)
    photo_consent = ConsentField(
        required=False, choices=constants.PHOTO_CONSENT_CHOICES
    )

    class Meta:
        model = Registration
        fields = (
            "id",
            "feedback",
            "presence",
            "photo_consent",
            "captcha_response",
            "charge_status",
        )

    def update(self, instance, validated_data):
        with transaction.atomic():
            presence = validated_data.pop("presence", None)
            super().update(instance, validated_data)
            if presence:
                instance.set_presence(presence)
            return instance


class RegistrationPublicReadSerializer(BasisModelSerializer):
    user = PublicUserSerializer()

    class Meta:
        model = Registration
        fields = ("id", "user", "pool", "status")
        read_only = True


class RegistrationReadSerializer(RegistrationPublicReadSerializer):
    feedback = PersonalFeedbackField()
    presence = PersonalPresenceField()
    photo_consent = PersonalConsentField()
    shared_memberships = serializers.IntegerField(required=False)

    class Meta(RegistrationPublicReadSerializer.Meta):
        fields = RegistrationPublicReadSerializer.Meta.fields + (
            "feedback",
            "shared_memberships",
            "presence",
            "photo_consent",
        )


class RegistrationSearchReadSerializer(RegistrationPublicReadSerializer):
    class Meta(RegistrationPublicReadSerializer.Meta):
        fields = RegistrationPublicReadSerializer.Meta.fields + (
            "presence",
            "photo_consent",
        )


class RegistrationSearchSerializer(serializers.Serializer):
    username = serializers.CharField()


class RegistrationConsentSerializer(serializers.Serializer):
    username = serializers.CharField()
    photo_consent = serializers.CharField()


class RegistrationPaymentReadSerializer(RegistrationReadSerializer):
    charge_status = PersonalChargeStatusField()

    class Meta(RegistrationReadSerializer.Meta):
        fields = RegistrationReadSerializer.Meta.fields + ("charge_status",)


class RegistrationReadDetailedSerializer(BasisModelSerializer):
    user = AdministrateUserSerializer()

    class Meta:
        model = Registration
        fields = (
            "id",
            "user",
            "created_by",
            "updated_by",
            "pool",
            "event",
            "presence",
            "feedback",
            "status",
            "registration_date",
            "unregistration_date",
            "admin_registration_reason",
            "charge_id",
            "charge_status",
            "charge_amount",
            "charge_amount_refunded",
            "photo_consent",
        )
        read_only = True


class StripeTokenSerializer(serializers.Serializer):
    payment_intent_id = serializers.CharField()


class StripeMetaSerializer(serializers.Serializer):
    EVENT_ID = serializers.IntegerField()
    USER = serializers.CharField()
    EMAIL = serializers.EmailField()


class StripeObjectSerializer(serializers.Serializer):
    id = serializers.CharField()
    amount = serializers.IntegerField()
    amount_refunded = serializers.IntegerField()
    status = serializers.CharField()
    metadata = StripeMetaSerializer()
