from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from lego.apps.events.models import Event
from lego.apps.permissions.constants import EDIT


# Personal....Fields for registrations will only return values if the authenticated
# user "owns" the registrations Otherwise null will be returned
class PersonalFeedbackField(serializers.Field):
    def get_attribute(self, instance):
        return instance

    def to_representation(self, value):
        request = self.context.get("request", None)
        if request and request.user.is_authenticated and request.user == value.user:
            return value.feedback

        user = self.context.get("user", None)
        if user and user == value.user:
            return value.feedback
        return None


class PersonalConsentField(serializers.Field):
    def get_attribute(self, instance):
        return instance

    def to_representation(self, value):
        request = self.context.get("request", None)
        if request and request.user.is_authenticated and request.user == value.user:
            return value.photo_consent

        user = self.context.get("user", None)
        if user and user == value.user:
            return value.photo_consent
        return None


class PersonalPresenceField(serializers.Field):
    def get_attribute(self, instance):
        return instance

    def to_representation(self, value):
        request = self.context.get("request", None)
        if request and request.user.is_authenticated and request.user == value.user:
            return value.presence

        user = self.context.get("user", None)
        if user and user == value.user:
            return value.presence
        return None


class PersonalPaymentStatusField(serializers.Field):
    def get_attribute(self, instance):
        return instance

    def to_representation(self, value):
        request = self.context.get("request", None)
        if request and request.user.is_authenticated and request.user == value.user:
            return value.payment_status

        user = self.context.get("user", None)
        if user and user == value.user:
            return value.payment_status
        return None


class IsAdmittedField(serializers.Field):
    def get_attribute(self, instance):
        return instance

    def to_representation(self, value):
        request = self.context.get("request", None)
        if not request or not request.user.is_authenticated:
            return False
        return value.is_admitted(request.user)


class ActivationTimeField(serializers.Field):
    def get_attribute(self, instance):
        return instance

    def to_representation(self, value):
        request = self.context.get("request", None)
        if not request or not request.user.is_authenticated:
            return

        kwargs = {}
        cached_penalties = self.context.get("cached_penalties", None)
        if hasattr(value, "possible_pools") and hasattr(value, "user_reg"):
            kwargs["pools"] = [] if value.user_reg else value.possible_pools
        if cached_penalties is not None:
            kwargs["penalties"] = cached_penalties
        return value.get_earliest_registration_time(request.user, **kwargs)


class SpotsLeftField(serializers.Field):
    def get_attribute(self, instance):
        return instance

    def to_representation(self, value):
        request = self.context.get("request", None)
        if request and request.user.is_authenticated:
            return value.spots_left_for_user(request.user)


class SetPaymentStatusField(serializers.ChoiceField):
    def get_attribute(self, instance):
        return instance

    def to_representation(self, value):
        request = self.context.get("request", None)
        if (
            request
            and request.user.is_authenticated
            and request.user.has_perm(EDIT, Event)
        ):
            return getattr(value, "payment_status", None)

    def to_internal_value(self, data):
        request = self.context.get("request", None)
        if (
            request
            and request.user.is_authenticated
            and request.user.has_perm(EDIT, Event)
        ):
            return super().to_internal_value(data)
        raise PermissionDenied()


class PresenceField(serializers.ChoiceField):
    def get_attribute(self, instance):
        return instance

    def to_representation(self, value):
        request = self.context.get("request", None)
        if (
            request
            and request.user.is_authenticated
            and request.user.has_perm(EDIT, Event)
        ):
            return getattr(value, "presence", None)

    def to_internal_value(self, data):
        request = self.context.get("request", None)
        if (
            request
            and request.user.is_authenticated
            and request.user.has_perm(EDIT, Event)
        ):
            return super().to_internal_value(data)
        raise PermissionDenied()


class ConsentField(serializers.ChoiceField):
    def get_attribute(self, instance):
        return instance

    def to_representation(self, value):
        request = self.context.get("request", None)
        if (
            request
            and request.user.is_authenticated
            and request.user.has_perm(EDIT, Event)
        ):
            return getattr(value, "photo_consent", None)

    def to_internal_value(self, data):
        request = self.context.get("request", None)
        if (
            request
            and request.user.is_authenticated
            and request.user.has_perm(EDIT, Event)
        ):
            return super().to_internal_value(data)
        raise PermissionDenied()


class PublicEventField(serializers.PrimaryKeyRelatedField):
    def use_pk_only_optimization(self):
        return False

    def to_representation(self, value):
        from lego.apps.events.serializers.events import EventPublicSerializer

        serializer = EventPublicSerializer(instance=value)
        return serializer.data


class PublicEventListField(serializers.ManyRelatedField):
    def __init__(self, field_kwargs=None, **kwargs):
        if field_kwargs is None:
            field_kwargs = {}

        kwargs["child_relation"] = PublicEventField(**field_kwargs)
        super().__init__(**kwargs)
