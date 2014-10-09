# -*- coding: utf8 -*-
import math

from django.test import TestCase
from django.core import mail as djangomail
from django.conf import settings

from lego.app.mail.logic import send_message


class LogicTestCase(TestCase):
    def setUp(self):
        pass

    def test_sendmail_simple(self):
        sender = 'dummy@abakus.no'
        recipients = ['user1@abakus.no', 'user2@abakus.no']
        message = djangomail.EmailMessage(
            'AbakusMailTest',
            'Testbody',
            sender,
            recipients,
            [],
            headers={}
        )
        send_message(message, recipients, sender)
        outbox = getattr(djangomail, 'outbox', [])

        self.assertEqual(outbox[0].from_email, sender)
        self.assertEqual(outbox[0].to, recipients)

    def test_sendmail_unvalid_sender(self):
        sender = 'dummytest'
        recipients = ['user1@abakus.no', 'user2@abakus.no']
        message = djangomail.EmailMessage(
            'AbakusMailTest',
            'Testbody',
            sender,
            recipients,
            [],
            headers={}
        )

        outbox = getattr(djangomail, 'outbox', [])
        old_outbox_len = len(outbox)
        send_res = send_message(message, recipients, sender)
        outbox = getattr(djangomail, 'outbox', [])

        self.assertEqual(send_res, False)
        self.assertEqual(len(outbox), old_outbox_len)

    def test_sendmail_no_recipients(self):
        sender = 'dummy@abakus.no'
        recipients = []
        message = djangomail.EmailMessage(
            'AbakusMailTest',
            'Testbody',
            sender,
            recipients,
            [],
            headers={}
        )

        outbox = getattr(djangomail, 'outbox', [])
        old_outbox_len = len(outbox)
        send_message(message, recipients, sender)
        outbox = getattr(djangomail, 'outbox', [])
        self.assertEqual(old_outbox_len, len(outbox))

    def test_sendmail_many_recipients(self):
        recipients_count = 404
        sender = 'dummy@abakus.no'
        recipients = ['user%s@abakus.no' % userID for userID in range(recipients_count)]
        message = djangomail.EmailMessage(
            'AbakusMailTest',
            'Testbody',
            sender,
            recipients,
            [],
            headers={}
        )

        send_message(message, recipients, sender)
        outbox = getattr(djangomail, 'outbox', [])
        batches = math.ceil(recipients_count/settings.MAIL_BATCH_LENGTH)
        self.assertEqual(len(outbox), batches)
