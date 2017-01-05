from rest_framework import serializers


class ApplicationField(serializers.PrimaryKeyRelatedField):

    def use_pk_only_optimization(self):
        return False

    def to_representation(self, value):
        return {
            'id': value.id,
            'name': value.name,
            'description': value.description
        }


class ProtectedTokenField(serializers.CharField):
    """
    This field is used to protect tokens. This makes it possible for users to identify tokens,
    but not use it after the creation.
    """
    def to_representation(self, value):
        start_token = '*' * 20
        end_token = value[:10]
        return f'{start_token}{end_token}'
