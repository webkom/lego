import json

from djangorestframework_camel_case.render import camelize


def notify_group(group, message):
    """
    Dumps the message to JSON and sends it to the specified channel.

    :param group: channels.Group
    :param message:
    """
    return group.send({'text': json.dumps(camelize(message))})
