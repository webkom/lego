from rest_framework import authentication, exceptions

from lego.apps.surveys.models import Survey


class SurveyTokenAuthentication(authentication.TokenAuthentication):
    keyword = 'Token'

    def authenticate_credentials(self, key):
        print('in here')
        try:
            survey = Survey.objects.get(token=key)
            print('token good')
        except Survey.DoesNotExist:
            print('token bad')
            raise exceptions.AuthenticationFailed('Invalid token')

        return None, survey
