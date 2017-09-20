from smtplib import SMTPException

import celery
from push_notifications import NotificationError
from structlog import get_logger

from lego import celery_app
from lego.apps.stats.statsd_client import statsd

from .email import EmailMessage
from .push import PushMessage

log = get_logger()


class AbakusTask(celery.Task):
    """
    This base task supplies the logger_context to the underlying worker.


    > @celery_app.task(bind=True, base=AbakusTask)
    > def task_name(self, logger_context=None):
    >    self.setup_logger(logger_context)
    >    other work...
    """

    def apply_async(self, args=None, kwargs=None, *arguments, **keyword_arguments):
        logger = log.bind()
        logger_context = dict(logger._context._dict)
        kwargs['logger_context'] = logger_context

        async_result = super().apply_async(args, kwargs, *arguments, **keyword_arguments)
        log.info('async_task_created', task_id=async_result.id, task_name=self.name)
        return async_result

    def setup_logger(self, logger_context):
        logger_context = logger_context or {}
        logger_context['task_name'] = self.name
        logger_context['task_id'] = self.request.id
        self.logger = log.new(**logger_context)


@celery_app.task(bind=True, max_retries=5, base=AbakusTask)
@statsd.timer('task.send_email')
def send_email(self, logger_context=None, **kwargs):
    """
    Generic task to send emails with retries.
    """
    self.setup_logger(logger_context)

    message = EmailMessage(**kwargs)

    try:
        message.send()
    except SMTPException as e:
        log.error('email_task_exception', exc_info=True, extra=kwargs)
        raise self.retry(exc=e, countdown=2 ** self.request.retries)


@celery_app.task(bind=True, max_retries=5, base=AbakusTask)
@statsd.timer('task.send_push')
def send_push(self, logger_context=None, **kwargs):
    """
    Generic task to send push messages.
    """
    self.setup_logger(logger_context)

    message = PushMessage(**kwargs)

    try:
        message.send()
    except NotificationError as e:
        log.error('push_task_exception', exec_info=True, extra=kwargs)
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
