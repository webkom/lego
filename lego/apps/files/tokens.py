from datetime import date

from django.utils import six
from django.utils.crypto import constant_time_compare, salted_hmac
from django.utils.http import base36_to_int, int_to_base36


class RedirectTokenGenerator(object):
    """
    Token generator for upload success redirects
    """
    key_salt = "lego_files_noetikon"
    valid_timedelta = 60*60

    def make_token(self, file):
        """
        Returns a token that can be used once to do a file upload success notification.
        """
        return self._make_token_with_timestamp(file, self._num_seconds(self._today()))

    def check_token(self, file, token):
        """
        Check that a password reset token is correct for a given file.
        """
        # Parse the token
        try:
            ts_b36, hash = token.split("-")
        except ValueError:
            return False

        try:
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        # Check that the timestamp/file id has not been tampered with
        if not constant_time_compare(self._make_token_with_timestamp(file, ts), token):
            return False

        # Check the timestamp is within limit
        if (self._num_seconds(self._today()) - ts) > self.valid_timedelta:
            return False

        return True

    def _make_token_with_timestamp(self, file, timestamp):
        ts_b36 = int_to_base36(timestamp)
        hash = salted_hmac(
            self.key_salt,
            self._make_hash_value(file, timestamp),
        ).hexdigest()[::2]
        return "%s-%s" % (ts_b36, hash)

    def _make_hash_value(self, file, timestamp):
        return (
            six.text_type(file.pk) + six.text_type(file.updated_at) + six.text_type(timestamp)
        )

    def _num_seconds(self, dt):
        return (dt - date(2001, 1, 1)).seconds

    def _today(self):
        # Used for mocking in tests
        return date.today()
