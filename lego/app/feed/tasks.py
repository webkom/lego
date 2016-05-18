from lego.settings import celery_app

from .feeds import NotificationFeed


@celery_app.task()
def notifications_mark_all(feed_id, seen=False, read=False):
    feed = NotificationFeed(feed_id)
    feed.mark_all(seen, read)


@celery_app.task()
def notifications_mark(feed_id, pk, seen=False, read=False):
    feed = NotificationFeed(feed_id)
    feed.mark_activity(pk, seen, read)
