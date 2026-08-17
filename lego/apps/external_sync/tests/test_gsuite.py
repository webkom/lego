import inspect
import re
from unittest import mock

from lego.apps.external_sync.utils import gsuite
from lego.apps.external_sync.utils.gsuite import GSuiteLib
from lego.utils.test_utils import BaseTestCase

NUM_RETRIES = 5


@mock.patch.object(GSuiteLib, "get_credentials", return_value=None)
@mock.patch("lego.apps.external_sync.utils.gsuite.build")
class GSuiteRetryTestCase(BaseTestCase):
    def test_get_user_asks_the_client_to_retry(self, build_mock, credentials_mock):
        lib = GSuiteLib()

        lib.get_user("test@abakus.no")

        execute = build_mock.return_value.users.return_value.get.return_value.execute
        execute.assert_called_once_with(num_retries=NUM_RETRIES)

    def test_get_group_asks_the_client_to_retry(self, build_mock, credentials_mock):
        lib = GSuiteLib()

        lib.get_group("abakom@abakus.no")

        execute = build_mock.return_value.groups.return_value.get.return_value.execute
        execute.assert_called_once_with(num_retries=NUM_RETRIES)

    def test_no_api_call_is_left_without_retries(self, build_mock, credentials_mock):
        """
        The Directory API returns transient 503s regularly, and a call without
        num_retries aborts the whole sync run partway through.
        """
        source = inspect.getsource(gsuite)

        self.assertEqual(re.findall(r"\.execute\(\s*\)", source), [])
        self.assertEqual(
            len(re.findall(r"\.execute\(num_retries=", source)),
            source.count(".execute("),
        )
