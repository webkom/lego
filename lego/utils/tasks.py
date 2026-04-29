from smtplib import SMTPException

from celery.app.task import Task
from push_notifications.exceptions import NotificationError
from structlog import get_context, get_logger

from lego import celery_app
from lego.apps.users.models import User

from .email import EmailMessage
from .push import PushMessage

log = get_logger()


class AbakusTask(Task):
    """
    This base task supplies the logger_context to the underlying worker.


    > @celery_app.task(bind=True, base=AbakusTask)
    > def task_name(self, logger_context=None):
    >    self.setup_logger(logger_context)
    >    other work...
    """

    def apply_async(self, args=None, kwargs=None, *arguments, **keyword_arguments):
        logger = log.bind()
        logger_context = dict(get_context(logger)._dict)
        kwargs["logger_context"] = logger_context

        async_result = super().apply_async(
            args, kwargs, *arguments, **keyword_arguments
        )
        log.info("async_task_created", task_id=async_result.id, task_name=self.name)
        return async_result

    def setup_logger(self, logger_context):
        logger_context = logger_context or {}
        logger_context["task_name"] = self.name
        logger_context["task_id"] = self.request.id
        self.logger = log.new(**logger_context)


@celery_app.task(bind=True, max_retries=5, base=AbakusTask)
def send_email(self, logger_context=None, **kwargs):
    """
    Generic task to send emails with retries.
    """
    self.setup_logger(logger_context)

    message = EmailMessage(**kwargs)

    try:
        message.send()
    except SMTPException as e:
        log.error("email_task_exception", exc_info=True, extra=kwargs)
        raise self.retry(exc=e, countdown=2**self.request.retries) from e


@celery_app.task(bind=True, max_retries=5, base=AbakusTask)
def send_push(self, user, title, target=None, logger_context=None, **kwargs):
    """
    Generic task to send push messages.
    """
    self.setup_logger(logger_context)

    recipient = User.objects.get(id=user)
    kwargs["user"] = recipient
    kwargs["target"] = target
    kwargs["title"] = title

    message = PushMessage(**kwargs)

    try:
        message.send()
    except NotificationError as e:
        log.error("push_task_exception", exec_info=True, extra=kwargs)
        raise self.retry(exc=e, countdown=2**self.request.retries) from e
