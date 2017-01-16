from rest_framework import serializers


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
