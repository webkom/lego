from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from lego.apps.email.models import EmailAddress, EmailList


class EmailAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmailAddress
        fields = ('email',)


class EmailListSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmailList
        fields = ('id', 'email_address', 'users', 'groups')

    def check_email_in_use(self, validated_data, instance=None):
        if 'email_address' in validated_data and validated_data['email_address'].is_assigned:
            if instance is None or instance.email_address != validated_data['email_address']:
                raise ValidationError('email is already assigned to somebody else')

    def create(self, validated_data):
        self.check_email_in_use(validated_data)
        return super(EmailListSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        self.check_email_in_use(validated_data, instance)
        return super(EmailListSerializer, self).update(instance, validated_data)
