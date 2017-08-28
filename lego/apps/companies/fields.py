from rest_framework import serializers


class SemesterField(serializers.PrimaryKeyRelatedField):

    def use_pk_only_optimization(self):
        return False

    def to_representation(self, value):
        from lego.apps.companies.serializers import SemesterSerializer
        serializer = SemesterSerializer(instance=value)
        return serializer.data


class CompanyField(serializers.PrimaryKeyRelatedField):

    def use_pk_only_optimization(self):
        return False

    def to_representation(self, value):
        from lego.apps.companies.serializers import CompanyListSerializer
        serializer = CompanyListSerializer(instance=value)
        return serializer.data


class CompanyContactField(serializers.PrimaryKeyRelatedField):

    def use_pk_only_optimization(self):
        return False

    def to_representation(self, value):
        from lego.apps.companies.serializers import CompanyContactSerializer
        serializer = CompanyContactSerializer(instance=value)
        return serializer.data
