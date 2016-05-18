from rest_framework import serializers

from .models import SearchTestModel


class SearchTestModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = SearchTestModel
        fields = ('title', 'description')
