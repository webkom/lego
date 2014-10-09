# -*- coding: utf8 -*-


MAIL_SENDMAIL_EXECUTABLE = '/usr/sbin/sendmail'
MAIL_BATCH_LENGTH = 50

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
