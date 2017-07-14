from .constants import RESTRICTED_TOKEN_PREFIX

PREFIX_LENGTH = len(RESTRICTED_TOKEN_PREFIX)


def get_mail_token(message):
    """
    Retrieve and delete restricted token if present.
    Returns:
    - modified message if key was present
    - None if key was not present
    """

    def get_and_delete_token(message, i):
        message_payload = message.get_payload(i).get_payload(decode=True)
        if message_payload is None and len(message_payload) > PREFIX_LENGTH:
            return

        message_payload = message_payload.decode()

        if message_payload[0:PREFIX_LENGTH] == RESTRICTED_TOKEN_PREFIX:
            del message.get_payload()[i]
            return message_payload[PREFIX_LENGTH:].strip()

    if message.is_multipart():
        for i in range(len(message.get_payload())):
            if message.get_payload(i).is_multipart():
                token = get_mail_token(message.get_payload(i))
                if token:
                    return token
            else:
                token = get_and_delete_token(message, i)
                if token:
                    return token
