from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from lego.apps.events.models import Registration


class ChargeStatusField(serializers.Field):

    def __init__(self, **kwargs):
        kwargs['source'] = '*'
        kwargs['read_only'] = True
        super().__init__(**kwargs)

    def to_representation(self, value):
        request = self.context.get('request', None)
        if request:
            if request.user.is_authenticated() and request.user == value.user:
                return value.charge_status
        socket_registration = self.context.get('registration', None)
        if socket_registration:
            registration = Registration.objects.get(pk=socket_registration)
            return registration.charge_status
            # Add admin permissions


class ActivationTimeField(serializers.Field):

    def __init__(self, **kwargs):
        kwargs['source'] = '*'
        kwargs['read_only'] = True
        super().__init__(**kwargs)

    def to_representation(self, value):
        request = self.context.get('request', None)
        if request and request.user.is_authenticated():
            return value.get_earliest_registration_time(request.user)


class SpotsLeftField(serializers.Field):

    def __init__(self, **kwargs):
        kwargs['source'] = '*'
        kwargs['read_only'] = True
        super().__init__(**kwargs)

    def to_representation(self, value):
        request = self.context.get('request', None)
        if request and request.user.is_authenticated():
            return value.spots_left_for_user(request.user)


class SetChargeStatusField(serializers.ChoiceField):

    def get_attribute(self, instance):
        return instance

    def to_representation(self, value):
        request = self.context.get('request', None)
        if request and request.user.is_authenticated and \
                request.user.has_perm('/sudo/admin/events/update/'):
            return getattr(value, 'charge_status', None)

    def to_internal_value(self, data):
        request = self.context.get('request', None)
        if request and request.user.is_authenticated and \
                request.user.has_perm('/sudo/admin/events/update/'):
            return super().to_internal_value(data)
        raise PermissionDenied()
