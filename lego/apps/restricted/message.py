from django.core.mail.message import MIMEMixin


class EmailMessage:
    """
    This class has the required properties and functions required to send a raw EmailMessage with
    the builtin django email backend.
    """

    def __init__(self, recipient, sender, message):
        self.recipient = recipient
        self.from_email = sender
        self.msg = message
        self.encoding = None
        self.msg['To'] = recipient

    def recipients(self):
        return [self.recipient]

    def message(self):
        """
        Return the message extended with the MIMEMixin.
        The MIMEMixin contains a custom as_bytes function required by django.
        """
        return self.extend_instance(self.msg, MIMEMixin)

    @staticmethod
    def extend_instance(obj, cls):
        """Apply mixin to a class instance after creation"""
        base_cls = obj.__class__
        base_cls_name = obj.__class__.__name__
        obj.__class__ = type(base_cls_name, (cls, base_cls), {})
        return obj
