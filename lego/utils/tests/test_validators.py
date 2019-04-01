import re

from lego.utils.test_utils import BaseTestCase
from lego.utils.youtube_validator import youtube_validator

correct_urls = [
    "https://www.youtube.com/watch?v=KrzIaRwAMvc",
    "https://youtu.be/KrzIaRwAMvc",
    "https://youtu.be/KrzIaRwAMvc?t=110",
    "www.youtube.com/watch?v=KrzIaRwAMvc",
    "youtube.com/watch?v=KrzIaRwAMvc",
    "youtu.be/KrzIaRwAMvc",
]

wrong_urls = [
    "https://www.skra.com/watch?v=KrzIaRwAMvc",
    "https://sk.ra/KrzIaRwAMvc",
    "https://bo.m/KrzIaRwAMvc?t=110",
    "www.skra.com/watch?v=KrzIaRwAMvc",
    "skra.com/watch?v=KrzIaRwAMvc",
    "sk.ra/KrzIaRwAMvc",
]


class YoutubeUrlValidatorTestCase(BaseTestCase):
    def setUp(self):
        self.regex = youtube_validator.regex

    def test_correct_urls(self):
        for url in correct_urls:
            match = re.search(self.regex, url)
            self.assertTrue(match)

    def test_wrong_urls(self):
        for url in wrong_urls:
            match = re.search(self.regex, url)
            self.assertFalse(match)
