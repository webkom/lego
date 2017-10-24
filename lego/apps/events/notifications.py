from lego.apps.notifications.constants import (EVENT_ADMIN_REGISTRATION, EVENT_BUMP,
                                               EVENT_PAYMENT_OVERDUE, EVENT_PAYMENT_OVERDUE_CREATOR)
from lego.apps.notifications.notification import Notification


class EventBumpNotification(Notification):

    name = EVENT_BUMP

    def generate_mail(self):
        event = self.kwargs['event']

        return self._delay_mail(
            to_email=self.user.email,
            context={
                'event': event.title,
                'name': self.user.full_name,
                'id': event.id,
            },
            subject=f'Du er flyttet opp fra ventelisten på arrangementet {event.title}',
            plain_template='events/email/bump.txt',
            html_template='events/email/bump.html',
        )

    def generate_push(self):
        event = self.kwargs['event']

        return self._delay_push(
            template='events/push/bump.txt',
            context={
                'event': event.title,
            },
            instance=event
        )


class EventPaymentOverdueNotification(Notification):

    name = EVENT_PAYMENT_OVERDUE

    def generate_mail(self):
        event = self.kwargs['event']

        return self._delay_mail(
            to_email=self.user.email,
            context={
                'event': event.title,
                'name': self.user.full_name,
                'due_date': event.payment_due_date,
                'id': event.id,
            },
            subject=f'Du har ikke betalt påmeldingen på arrangementet {event.title}',
            plain_template='events/email/payment_overdue.txt',
            html_template='events/email/payment_overdue.html',
        )

    def generate_push(self):
        event = self.kwargs['event']

        return self._delay_push(
            template='events/push/payment_overdue.txt',
            context={
                'event': event.title,
            },
            instance=event
        )


class EventPaymentOverdueCreatorNotification(Notification):

    name = EVENT_PAYMENT_OVERDUE_CREATOR

    def generate_mail(self):
        event = self.kwargs['event']
        users = self.kwargs['users']

        return self._delay_mail(
            to_email=self.user.email,
            context={
                'event': event.title,
                'users': users,
                'name': self.user.full_name,
                'id': event.id,
            },
            subject=f'Følgende registrerte har ikke betalt påmeldingen til arrangementet'
                    f' {event.title}',
            plain_template='events/email/payment_overdue_author.txt',
            html_template='events/email/payment_overdue_author.html',
        )


class EventAdminRegistrationNotification(Notification):

    name = EVENT_ADMIN_REGISTRATION

    def generate_mail(self):
        event = self.kwargs['event']
        reason = self.kwargs['reason']

        return self._delay_mail(
            to_email=self.user.email,
            context={
                'event': event.title,
                'name': self.user.full_name,
                'reason': reason,
                'id': event.id,
            },
            subject=f'Du har blitt adminpåmeldt på arrangementet {event.title}',
            plain_template='events/email/admin_registration.txt',
            html_template='events/email/admin_registration.html',
        )

    def generate_push(self):
        event = self.kwargs['event']

        return self._delay_push(
            template='events/push/admin_registration.txt',
            context={
                'event': event.title,
            },
            instance=event
        )
