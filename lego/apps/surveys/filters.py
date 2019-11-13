from django_filters import CharFilter, FilterSet

from lego.apps.surveys.models import Submission, Survey


class SurveyFilterSet(FilterSet):
    company = CharFilter("event__company")

    class Meta:
        model = Survey
        fields = ("event",)


class SubmissionFilterSet(FilterSet):
    user = CharFilter("user")

    class Meta:
        model = Submission
        fields = ("user",)
