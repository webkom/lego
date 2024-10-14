from lego import celery_app
from lego.apps.achievements.promotion import check_all_promotions
from lego.apps.events.tasks import AsyncRegister


@celery_app.task(base=AsyncRegister, bind=True)
def run_all_promotions(self, logger_context=None):
    self.setup_logger(logger_context)
    check_all_promotions()
