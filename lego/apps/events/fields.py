from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from lego.apps.events.models import Event
from lego.apps.permissions.constants import EDIT


class FeedbackField(serializers.Field):

    def get_attribute(self, instance):
        return instance

    def to_representation(self, value):
        request = self.context.get('request', None)
        if request and request.user.is_authenticated and request.user == value.user:
            return value.feedback

        user = self.context.get('user', None)
        if user and user == value.user:
            return value.feedback
        return None


class ChargeStatusField(serializers.Field):

    def get_attribute(self, instance):
        return instance

    def to_representation(self, value):
        request = self.context.get('request', None)
        if request and request.user.is_authenticated and request.user == value.user:
            return value.charge_status

        user = self.context.get('user', None)
        if user and user == value.user:
            return value.charge_status
        return None


class ActivationTimeField(serializers.Field):

    def get_attribute(self, instance):
        return instance

    def to_representation(self, value):
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            return value.get_earliest_registration_time(request.user)


class SpotsLeftField(serializers.Field):

    def get_attribute(self, instance):
        return instance

    def to_representation(self, value):
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            return value.spots_left_for_user(request.user)


class SetChargeStatusField(serializers.ChoiceField):

    def get_attribute(self, instance):
        return instance

    def to_representation(self, value):
        request = self.context.get('request', None)
        if request and request.user.is_authenticated and request.user.has_perm(EDIT, Event):
            return getattr(value, 'charge_status', None)

    def to_internal_value(self, data):
        request = self.context.get('request', None)
        if request and request.user.is_authenticated and request.user.has_perm(EDIT, Event):
            return super().to_internal_value(data)
        raise PermissionDenied()


class PresenceField(serializers.ChoiceField):

    def get_attribute(self, instance):
        return instance

    def to_representation(self, value):
        request = self.context.get('request', None)
        if request and request.user.is_authenticated and request.user.has_perm(EDIT, Event):
            return getattr(value, 'presence', None)

    def to_internal_value(self, data):
        request = self.context.get('request', None)
        if request and request.user.is_authenticated and request.user.has_perm(EDIT, Event):
            return super().to_internal_value(data)
        raise PermissionDenied()
