from lego.apps.polls.models import Poll
from lego.apps.users.models import User
from lego.utils.test_utils import BaseTestCase


class PollMethodTest(BaseTestCase):
    fixtures = ["test_users.yaml", "test_polls.yaml"]

    def setUp(self):
        self.user = User.objects.get(username="test1")
        self.poll = Poll.objects.get(pk=1)

    def test_str(self):
        title = "Test poll 1"
        self.assertEqual(str(self.poll), title)
