from lego import celery_app
from lego.apps.achievements.promotion import (
    check_all_promotions,
    check_event_related_single_user,
)
from lego.utils.tasks import AbakusTask


@celery_app.task(base=AbakusTask, bind=True)
def run_all_promotions(self, logger_context=None):
    self.setup_logger(logger_context)
    check_all_promotions()


@celery_app.task(base=AbakusTask, bind=True)
def async_check_event_achievements_single_user(
    self,
    user_id: int,
    logger_context=None,
):
    self.setup_logger(logger_context)
    check_event_related_single_user(user_id)
