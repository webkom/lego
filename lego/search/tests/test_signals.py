from unittest import mock

from django.test import TestCase, override_settings

from lego.search import signals


class SignalTestCase(TestCase):

    @override_settings(TESTING=False)
    @mock.patch('lego.search.signal_handler.SignalHandler.on_save')
    def test_handler_save(self, mock_on_save):
        sender_mock = mock.Mock()
        instance_mock = mock.Mock()
        created = True
        update_fields = ['name']
        signals.post_save_callback(sender=sender_mock, instance=instance_mock, created=created,
                                   update_fields=update_fields)

        mock_on_save.assert_called_once_with(sender_mock, instance_mock, created, update_fields)

    @override_settings(TESTING=False)
    @mock.patch('lego.search.signal_handler.SignalHandler.on_delete')
    def test_handler_delete(self, mock_on_save):
        sender_mock = mock.Mock()
        instance_mock = mock.Mock()
        signals.post_delete_callback(sender=sender_mock, instance=instance_mock)

        mock_on_save.assert_called_once_with(sender_mock, instance_mock)
