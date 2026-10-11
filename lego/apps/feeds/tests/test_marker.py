from unittest import mock

from django.test import SimpleTestCase

from lego.apps.feeds.marker import MarkerModelMixin

STORAGE = "lego.apps.feeds.marker.RedisListStorage"


class MarkerTestCase(SimpleTestCase):
    @mock.patch(STORAGE)
    def test_mark_all_without_flags_is_noop(self, storage):
        MarkerModelMixin.mark_all("1", seen=False, read=False)
        storage.assert_not_called()

    @mock.patch(STORAGE)
    def test_mark_all_seen_and_read(self, storage):
        MarkerModelMixin.mark_all("1", seen=True, read=True)
        storage.return_value.flush.assert_called_once_with("unseen", "unread")

    @mock.patch(STORAGE)
    def test_mark_activities_empty_is_noop(self, storage):
        MarkerModelMixin.mark_activities("1", [], seen=True, read=True)
        storage.assert_not_called()

    @mock.patch(STORAGE)
    def test_mark_activities_without_flags_is_noop(self, storage):
        MarkerModelMixin.mark_activities("1", ["1"], seen=False, read=False)
        storage.assert_not_called()

    @mock.patch(STORAGE)
    def test_mark_activities_converts_ids_to_str(self, storage):
        MarkerModelMixin.mark_activities("1", [10, 11], seen=True, read=True)
        storage.return_value.remove.assert_called_once_with(
            unseen=["10", "11"], unread=["10", "11"]
        )

    @mock.patch(STORAGE)
    def test_mark_activity_delegates_to_mark_activities(self, storage):
        MarkerModelMixin.mark_activity("1", 10, seen=True, read=True)
        storage.return_value.remove.assert_called_once_with(
            unseen=["10"], unread=["10"]
        )

    @mock.patch(STORAGE)
    def test_mark_insert_activity(self, storage):
        MarkerModelMixin.mark_insert_activity("1", 10)
        storage.return_value.add.assert_called_once_with(unseen=["10"], unread=["10"])
