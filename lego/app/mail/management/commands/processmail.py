# -*- coding: utf8 -*-
import email, sys, logging

from django.core.management.base import BaseCommand, CommandError

from lego.app.mail.logic import handle_mail


class Command(BaseCommand):

    help = "Processes a mail"
    args = '<recipients> <sender>'

    def handle(self, sender, *recipients, **options):
        try:
            msg = email.message_from_file(sys.stdin)
            for recipient in recipients:
                handle_mail(msg, sender, recipient)
        except Exception as ex:
            raise CommandError('The mail system can\'t process this mail. %s' % (str(ex), ))