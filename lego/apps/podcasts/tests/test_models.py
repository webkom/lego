from lego.utils.test_utils import BaseTestCase


class PodcastTest(BaseTestCase):
    """
    The podcast should default return the source as string
    """

    def test_str(self):
        self.assertEqual(str(self.podcast), self.podcast.source)
