from lego.apps.notifications.constants import SURVEY_CREATED
from lego.apps.notifications.notification import Notification


class SurveyNotification(Notification):
    name = SURVEY_CREATED

    def generate_mail(self):
        survey = self.kwargs["survey"]

        return self._delay_mail(
            to_email=self.user.email,
            context={
                "first_name": self.user.first_name,
                "survey": survey.id,
                "event": survey.event.title,
                "active_from": survey.active_from,
            },
            subject=f"Spørreundersøkelse for {survey.event.title}",
            plain_template="surveys/email/survey.txt",
            html_template="surveys/email/survey.html",
        )

    def generate_push(self):
        survey = self.kwargs["survey"]

        return self._delay_push(
            template="surveys/push/survey.txt",
            context={"event": survey.event.title},
            title="Spørreundersøkelse",
            instance=survey,
        )
