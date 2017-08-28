from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from structlog import get_logger

from lego.apps.stats.statsd_client import statsd

log = get_logger()


@receiver(post_save)
def post_save_callback(instance, created, **kwargs):
    app = instance._meta.app_label
    model = instance._meta.model_name

    if created:
        statsd.incr(f'instance.create.{app}.{model}', 1)
        log.info(
            'instance_create',
            app=app,
            model=model,
            pk=instance.pk
        )
    else:
        statsd.incr(f'instance.update.{app}.{model}', 1)
        log.info(
            'instance_update',
            app=app,
            model=model,
            pk=instance.pk
        )


@receiver(post_delete)
def post_delete_callback(instance, **kwargs):
    app = instance._meta.app_label
    model = instance._meta.model_name

    statsd.incr('instance.delete.{app}.{model}', 1)
    log.info(
        f'instance_delete',
        app=app,
        model=model,
        pk=instance.pk
    )
