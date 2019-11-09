from django.db import transaction
from rest_framework import serializers

from rest_framework_jwt.serializers import User

from lego.apps.events import constants
from lego.apps.events.fields import (
    ConsentField,
    PersonalConsentField,
    PersonalFeedbackField,
    PersonalPaymentStatusField,
    PersonalPresenceField,
    PresenceField,
    SetPaymentStatusField,
)
from lego.apps.events.models import Pool, Registration
# from lego.apps.events.tasks import async_cancel_payment
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
        max_length=Registration._meta.get_field("admin_registration_reason").max_length,
        required=True,
    )


class RegistrationCreateAndUpdateSerializer(BasisModelSerializer):
    captcha_response = serializers.CharField(required=False)
    payment_status = SetPaymentStatusField(
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
            "payment_status",
        )

    def update(self, instance, validated_data):
        with transaction.atomic():
            presence = validated_data.pop("presence", None)
            super().update(instance, validated_data)
            if presence:
                instance.set_presence(presence)

            # if validated_data["payment_status"] == constants.PAYMENT_MANUAL:
            # async_cancel_payment(instance.id).delay()

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
    payment_status = PersonalPaymentStatusField()

    class Meta(RegistrationReadSerializer.Meta):
        fields = RegistrationReadSerializer.Meta.fields + ("payment_status",)


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
            "payment_intent_id",
            "payment_status",
            "payment_amount",
            "payment_amount_refunded",
            "photo_consent",
        )
        read_only = True


class StripeMetaSerializer(serializers.Serializer):
    EVENT_ID = serializers.IntegerField()
    USER = serializers.CharField()
    EMAIL = serializers.EmailField()


class StripePaymentIntentErrorSerializer(serializers.Serializer):
    """
    Stripe payment intent last error.
    https://stripe.com/docs/api/payment_intents/object#payment_intent_object-last_payment_error
    """

    code = serializers.CharField()
    doc_url = serializers.CharField()
    message = serializers.CharField()
    type = serializers.CharField()


class StripePaymentIntentSerializer(serializers.Serializer):
    id = serializers.CharField()
    amount = serializers.IntegerField()
    status = serializers.CharField()
    metadata = StripeMetaSerializer()
    last_payment_error = StripePaymentIntentErrorSerializer(allow_null=True)


class StripeChargeSerializer(serializers.Serializer):
    id = serializers.CharField()
    amount = serializers.IntegerField()
    amount_refunded = serializers.IntegerField()
    status = serializers.CharField()
    metadata = StripeMetaSerializer()
