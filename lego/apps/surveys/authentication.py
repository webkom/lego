from rest_framework import authentication

from lego.apps.surveys.models import Survey
from lego.apps.users.models import User


class SurveyAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):

        raw_token = request.GET.get('token')
        if not raw_token:
            return

        try:
            Survey.objects.get(token=raw_token)
            return User.objects.get(
                pk=1
            ), raw_token  # TODO: Select a prod user for this or solve differently
        except Survey.DoesNotExist:
            pass

        return
