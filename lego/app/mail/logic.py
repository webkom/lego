


def handle_mail(msg, sender, recipient) -> (None):
    """
    Process mail.

    :param msg: email object
    :param sender: sender as string, local and global part.
    :param recipient: recipient as string, local and global part.
    :return: None
    """

    print(msg, sender, recipient)