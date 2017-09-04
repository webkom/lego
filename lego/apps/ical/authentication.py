from rest_framework import authentication

from lego.apps.ical.models import ICalToken


class ICalTokenAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):

        raw_token = request.GET.get('token')
        if not raw_token:
            return

        try:
            token = ICalToken.objects.get(token=raw_token)
            return token.user, raw_token
        except ICalToken.DoesNotExist:
            pass

        return
