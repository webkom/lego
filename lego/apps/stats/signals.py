from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from prometheus_client import Counter
from structlog import get_logger

from lego.apps.stats.instance_tracking import track_instance

log = get_logger()

INSTANCE_COUNTER = Counter(
    'instance_change',
    'Counts actions performed on an instance',
    ['action', 'app', 'model'],
)


@receiver(post_save)
def post_save_callback(instance, created, **kwargs):
    app = instance._meta.app_label
    model = instance._meta.model_name

    if created:
        INSTANCE_COUNTER.labels('create', app, model).inc(1)
        log.info('instance_create', app=app, model=model, pk=instance.pk)
    else:
        INSTANCE_COUNTER.labels('update', app, model).inc(1)
        log.info('instance_update', app=app, model=model, pk=instance.pk)

    track_instance(instance)


@receiver(post_delete)
def post_delete_callback(instance, **kwargs):
    app = instance._meta.app_label
    model = instance._meta.model_name

    INSTANCE_COUNTER.labels('delete', app, model).inc(1)
    log.info(f'instance_delete', app=app, model=model, pk=instance.pk)
