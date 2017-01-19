from rest_framework import serializers


class QuerySerializer(serializers.Serializer):
    query = serializers.CharField()
    types = serializers.ListField(child=serializers.CharField(), default=[])
    filters = serializers.DictField(
        child=serializers.ListField(child=serializers.CharField()),
        default={}
    )


class AutocompleteSerializer(serializers.Serializer):
    query = serializers.CharField()
    types = serializers.ListField(child=serializers.CharField(), default=[])
