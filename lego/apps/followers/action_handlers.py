from lego.apps.users.notifications import PenaltyNotification, PenaltyTest


notification = PenaltyTest(instance.user, penalty=instance)
notification.notify()
