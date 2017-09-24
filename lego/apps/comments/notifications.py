from lego.apps.notifications.constants import COMMENT, COMMENT_REPLY
from lego.apps.notifications.notification import Notification


class CommentNotification(Notification):

    name = COMMENT

    def generate_mail(self):

        target = str(self.kwargs['target'])
        author = self.kwargs['author']

        return self._delay_mail(
            to_email=self.user.email,
            context={
                'name': self.user.full_name,
                'target': target,
                'author_name': author.full_name
            },
            subject=f'{author.full_name} har kommentert på {target}',
            plain_template='comments/email/comment.txt',
            html_template='comments/email/comment.html',
        )


class CommentReplyNotification(Notification):

    name = COMMENT_REPLY

    def generate_mail(self):

        target = str(self.kwargs['target'])
        author = self.kwargs['author']

        return self._delay_mail(
            to_email=self.user.email,
            context={
                'name': self.user.full_name,
                'target': target,
                'author_name': author.full_name
            },
            subject=f'{author.full_name} har svart på kommentaren din på {target}',
            plain_template='comments/email/comment_reply.txt',
            html_template='comments/email/comment_reply.html',
        )
