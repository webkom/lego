from lego.apps.feed.feed import NotificationFeed as BaseNotificationFeed


class NotificationFeed(BaseNotificationFeed):

    timeline_cf_name = 'notification'
