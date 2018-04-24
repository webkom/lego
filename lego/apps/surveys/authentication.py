from rest_framework import authentication, exceptions

from lego.apps.surveys.models import Survey


class SurveyTokenAuthentication(authentication.TokenAuthentication):
    keyword = 'Token'

    def authenticate_credentials(self, key):
        try:
            survey = Survey.objects.get(token=key)
        except Survey.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token')

        return None, survey
