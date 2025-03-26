from lego.apps.notifications.constants import COMMENT_REPLY
from lego.apps.notifications.notification import Notification


class CommentReplyNotification(Notification):
    name = COMMENT_REPLY

    def generate_mail(self):
        target = self.kwargs["target"]
        target_string = str(target)
        author = self.kwargs["author"]
        text = self.kwargs["text"]

        return self._delay_mail(
            to_email=self.user.email,
            context={
                "first_name": self.user.first_name,
                "target": target_string,
                "author_name": author.full_name,
                "text": text,
                "url": target.get_absolute_url(),
            },
            subject=f"{author.full_name} har svart på kommentaren din på {target_string}",
            plain_template="comments/email/comment_reply.txt",
            html_template="comments/email/comment_reply.html",
        )
