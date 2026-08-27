from lego import celery_app
from lego.apps.achievements.constants import RankType
from lego.apps.achievements.promotion import (
    check_all_promotions,
    check_event_related_single_user,
)
from lego.apps.achievements.ranking import snapshot_rank_type
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


@celery_app.task(base=AbakusTask, bind=True)
def snapshot_leaderboard_ranks(self, logger_context=None):
    """
    Runs daily. For each rank type, diffs today's computed ranking against
    the most recent stored snapshot per user and only writes rows for users
    whose rank actually changed.
    """
    self.setup_logger(logger_context)
    for rank_type in RankType.values:
        created = snapshot_rank_type(rank_type)
        self.logger.info(
            f"Snapshotted {rank_type} ranks",
            extra={"rank_type": rank_type, "rows_created": created},
        )
