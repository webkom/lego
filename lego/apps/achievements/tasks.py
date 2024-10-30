from lego import celery_app
from lego.apps.achievements.promotion import (
    check_all_promotions,
    check_event_related_single_user,
)
from lego.apps.events.tasks import AsyncRegister


@celery_app.task(base=AsyncRegister, bind=True)
def run_all_promotions(self, logger_context=None):
    self.setup_logger(logger_context)
    check_all_promotions()


@celery_app.task(base=AsyncRegister, bind=True)
def async_check_event_achievements_single_user(
    self,
    user,
    logger_context=None,
):
    self.setup_logger(logger_context)
    check_event_related_single_user(user)
