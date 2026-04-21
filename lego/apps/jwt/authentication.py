from django.utils import timezone

from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from structlog import get_logger

from lego.apps.users.models import User

log = get_logger()


class Authentication(JSONWebTokenAuthentication):
    """
    Attach the JWT user to the log context.
    """

    def authenticate(self, request):
        authentication = super().authenticate(request)

        if authentication:
            user = authentication[0]
            log.bind(current_user=user.id)
            current_time = timezone.now()
            User.objects.filter(pk=user.pk).update(
                last_login=current_time, inactive_notified_counter=0
            )
            user.last_login = current_time
            user.inactive_notified_counter = 0

        return authentication
