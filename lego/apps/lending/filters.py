from django_filters.rest_framework import FilterSet

from lego.apps.lending.models import LendableObject, LendingInstance


class LendableObjectFilterSet(FilterSet):
    class Meta:
        model = LendableObject
        fields = ["title"]


class LendingInstanceFilterSet(FilterSet):
    class Meta:
        model = LendingInstance
        fields = [
            "user",
            "lendable_object",
            "start_date",
            "pending",
        ]
