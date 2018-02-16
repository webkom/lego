from django_filters import CharFilter, FilterSet

from lego.apps.surveys.models import Submission


class SubmissionFilterSet(FilterSet):
    user = CharFilter('user')

    class Meta:
        model = Submission
        fields = ('user', )
