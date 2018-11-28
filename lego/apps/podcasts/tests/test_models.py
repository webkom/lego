from lego.apps.podcasts.models import Podcast
from lego.apps.users.models import User
from lego.utils.test_utils import BaseTestCase


class PodcastMethodTest(BaseTestCase):
    fixtures = ["test_users.yaml", "test_podcasts.yaml"]

    def setUp(self):
        self.user = User.objects.get(username="test1")
        self.podcast = Podcast.objects.get(pk=1)

    def test_str(self):
        source = "https://soundcloud.com/user-279926342/20-slutten-pa-en-aera"
        self.assertEqual(str(self.podcast), source)
