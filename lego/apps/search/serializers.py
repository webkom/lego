from rest_framework import serializers

# Bound the anonymous search endpoints: an unbounded query crashes Postgres'
# tsquery parser ("stack depth limit exceeded") and an unbounded types list
# multiplies full-table scans.
MAX_QUERY_LENGTH = 500
MAX_TYPES = 32


class QuerySerializer(serializers.Serializer):
    query = serializers.CharField(max_length=MAX_QUERY_LENGTH)
    types = serializers.ListField(
        child=serializers.CharField(max_length=100), default=[], max_length=MAX_TYPES
    )
    filters = serializers.DictField(
        child=serializers.ListField(child=serializers.CharField()), default={}
    )


class AutocompleteSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=MAX_QUERY_LENGTH)
    types = serializers.ListField(
        child=serializers.CharField(max_length=100), default=[], max_length=MAX_TYPES
    )
