from unittest import mock

from django.db import models

from lego.utils.models import PersistentModel, TimeStampModel
from lego.utils.test_utils import BaseTestCase


class TestTimeStampModel(TimeStampModel):
    name = models.CharField("name", max_length=30)


class TestPersistentModel(PersistentModel):
    name = models.CharField("name", max_length=30)


class TimeStampModelTestCase(BaseTestCase):
    def setUp(self):
        self.instance = TestTimeStampModel()

    @mock.patch("lego.utils.models.timezone.now")
    @mock.patch("lego.utils.models.models.Model.save")
    def test_save(self, mock_save, mock_now):
        self.instance.save()
        self.assertEqual(self.instance.updated_at, mock_now.return_value)
        mock_save.assert_called_once_with()


class PersistentModelTestCase(BaseTestCase):
    def setUp(self):
        self.instance = TestPersistentModel()

    @mock.patch("lego.utils.models.models.Model.save")
    def test_restore(self, mock_save):
        self.instance.deleted = True
        self.instance.restore()
        self.assertFalse(self.instance.deleted)
        mock_save.assert_called_once_with()
