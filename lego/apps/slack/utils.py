import time

import requests
import structlog
from django.conf import settings
from django.core.validators import ValidationError, validate_email

log = structlog.get_logger()


class SlackException(Exception):
    pass


class SlackInvite:

    def __init__(self):
        self.token = settings.SLACK_TOKEN
        self.team_name = settings.SLACK_TEAM

    def _url(self):
        return 'https://{team}.slack.com/api/users.admin.invite?t={time}'.format(
            team=self.team_name, time=int(time.time())
        )

    def _post(self, email):
        response = requests.post(self._url(), data={
            'email': email,
            'token': self.token,
            'set_active': 'true',
            '_attempts': 1
        })
        if not response.ok:
            raise SlackException('invitation_failed')
        data = response.json()
        if not data['ok']:
            raise SlackException(data['error'])

    def invite(self, email):
        try:
            validate_email(email)
            self._post(email)
            log.info('slack_invite_sent', email=email)
        except ValidationError:
            raise SlackException('invalid_email')
