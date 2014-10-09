# -*- coding: utf8 -*
import subprocess
from copy import copy

from django.conf import settings
from django.core import mail as djangomail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


def __sendmail(args, msg):
    if settings.EMAIL_BACKEND == 'django.core.mail.backends.locmem.EmailBackend':
        # msg['X-args'] = args[1:]
        djangomail.get_connection(fail_silently=False).send_messages((msg,))
    else:
        process = subprocess.Popen(args, stdin=subprocess.PIPE, close_fds=True)
        process.stdin.write(msg.as_string())
        process.stdin.close()


def send_message(message, addresses, sender):
    try:
        validate_email(sender)
        common_arguments = [settings.MAIL_SENDMAIL_EXECUTABLE, '-G', '-i', '-f', sender]
        for i in range(0, len(addresses), settings.MAIL_BATCH_LENGTH):
            current_addresses = addresses[i: i+settings.MAIL_BATCH_LENGTH]
            current_arguments = copy(common_arguments)
            current_arguments.extend(current_addresses)
            __sendmail(current_arguments, message)
    except ValidationError:
        return False


def handle_mail(msg, sender, recipient):
    """
    Process mail.

    :param msg: email object
    :param sender: sender as string, local and global part.
    :param recipient: recipient as string, local and global part.
    :return: None
    """

    print(msg, sender, recipient)
