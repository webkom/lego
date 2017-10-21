from django.core.exceptions import ValidationError
from rest_framework import exceptions, serializers

from lego.apps.email.models import EmailAddress, EmailList
from lego.apps.users.fields import PublicUserField
from lego.apps.users.models import User

from .fields import EmailAddressField


class EmailListSerializer(serializers.ModelSerializer):

    email = EmailAddressField(read_only=True)

    class Meta:
        model = EmailList
        fields = ('id', 'name', 'email', 'users', 'groups', 'group_roles')


class EmailListCreateSerializer(EmailListSerializer):
    """
    It isn't possible to change the email after the list is created!

    TODO: This could be solved with group deletion, but this is'nt supported by the external_sync
    tool. Reuse lists for now! :D
    """
    email = EmailAddressField(queryset=EmailAddress.objects.all())


class GSuiteAddressSerializer(serializers.ModelSerializer):

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


class UserEmailSerializer(GSuiteAddressSerializer):

    user = PublicUserField(read_only=True, source='*')
    internal_email = EmailAddressField(queryset=EmailAddress.objects.all(), validators=[])

    class Meta:
        model = User
        fields = ('id', 'user', 'internal_email', 'internal_email_enabled')


class UserEmailCreateSerializer(serializers.Serializer):

    user = PublicUserField(queryset=User.objects.all())
    internal_email = EmailAddressField(queryset=EmailAddress.objects.all())
    internal_email_enabled = serializers.BooleanField()

    def create(self, validated_data):
        user = validated_data['user']
        internal_email = validated_data['internal_email']
        internal_email_enabled = validated_data['internal_email_enabled']

        user.internal_email = internal_email
        user.internal_email_enabled = internal_email_enabled
        user.save()

        return user

    def to_representation(self, instance):
        serializer = UserEmailSerializer(instance=instance)
        return serializer.data

    def validate_user(self, user):
        if user.internal_email_id is not None:
            raise exceptions.ValidationError('User already has a internal email.')
        return user
