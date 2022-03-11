from rest_framework import authentication, exceptions

from lego.apps.surveys.models import Survey


class SurveyTokenAuthentication(authentication.TokenAuthentication):
    keyword = "Token"

    def authenticate_credentials(self, key):
        try:
            survey = Survey.objects.get(token=key)
        except Survey.DoesNotExist as e:
            raise exceptions.AuthenticationFailed("Invalid token") from e

        return None, survey
