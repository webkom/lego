from django.db.models import Q
from django_filters import CharFilter, FilterSet, NumberFilter

from lego.apps.events.constants import PRESENCE_CHOICES
from lego.apps.surveys.models import Submission, Survey


class SurveyFilterSet(FilterSet):
    company = CharFilter("event__company")
    user = NumberFilter(method="filter_by_attended_user")

    class Meta:
        model = Survey
        fields = ("event",)

    def filter_by_attended_user(self, queryset, name, value):
        return queryset.filter(
            Q(event__registrations__user=value)
            & Q(event__registrations__presence=PRESENCE_CHOICES.PRESENT)
        )


class SubmissionFilterSet(FilterSet):
    user = CharFilter("user")

    class Meta:
        model = Submission
        fields = ("user",)
