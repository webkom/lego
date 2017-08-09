from django.core.exceptions import ValidationError
from rest_framework import serializers

from lego.apps.email.models import EmailAddress, EmailList
from lego.apps.users.models import AbakusGroup, User

from .fields import EmailAddressField


class EmailListSerializer(serializers.ModelSerializer):

    email = EmailAddressField(read_only=True)

    class Meta:
        model = EmailList
        fields = ('id', 'name', 'email', 'users', 'groups')


class EmailListCreateSerializer(EmailListSerializer):
    """
    It isn't possible to change the email after the list is created!

    TODO: This could be solved with group deletion, but this is'nt supported by the external_sync
    tool. Reuse lists for now! :D
    """
    email = EmailAddressField(queryset=EmailAddress.objects.all())


class UserEmailSerializer(serializers.ModelSerializer):

    internal_email = EmailAddressField(queryset=EmailAddress.objects.all(), validators=[])

    class Meta:
        model = User
        fields = ('id', 'username', 'internal_email', 'internal_email_enabled')
        read_only_fields = ('id', 'username')

    def validate(self, attrs):
        internal_email = attrs.get('internal_email')

        # Change a previous assigned internal_email
        if internal_email and self.instance.internal_email:
            if not internal_email == self.instance.internal_email:
                raise ValidationError('Cannot change a previous assigned internal_email')

        # Remove assigned internal_email
        if 'internal_email' in attrs.keys() and not internal_email:
            raise ValidationError('Cannot remove an assigned internal_email')

        # internal_email assigned to someone else
        if internal_email and internal_email.is_assigned(self.instance):
            raise ValidationError('The address is already assigned')

        return attrs


class AbakusGroupEmailSerializer(serializers.ModelSerializer):

    internal_email = EmailAddressField(queryset=EmailAddress.objects.all(), validators=[])

    class Meta:
        model = AbakusGroup
        fields = ('id', 'name', 'internal_email', 'internal_email_enabled')
        read_only_fields = ('id', 'name')

    def validate(self, attrs):
        internal_email = attrs.get('internal_email')

        # Change a previous assigned internal_email
        if internal_email and self.instance.internal_email:
            if not internal_email == self.instance.internal_email:
                raise ValidationError('Cannot change a previous assigned internal_email')

        # Remove assigned internal_email
        if 'internal_email' in attrs.keys() and not internal_email:
            raise ValidationError('Cannot remove an assigned internal_email')

        # internal_email assigned to someone else
        if internal_email and internal_email.is_assigned(self.instance):
            raise ValidationError('The address is already assigned')

        return attrs
