from lego.apps.feed.feed_handlers.base_handler import BaseHandler
from lego.apps.feed.feed_manager import feed_manager
from lego.apps.feed.registry import register_handler
from lego.apps.restricted.models import RestrictedMail


class RestrictedHandler(BaseHandler):

    model = RestrictedMail
    manager = feed_manager

    def handle_create(self, restricted_mail):
        pass

    def handle_update(self, restricted_mail):
        pass

    def handle_delete(self, restricted_mail):
        pass

    def handle_process_message(self, restricted_mail):
        pass


register_handler(RestrictedHandler)
