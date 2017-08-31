from . import constants


def action_to_permission(action):
    """
    The api has some built-in actions, convert these to internal permissions or return custom
    ones.
    """

    action_map = {
        'list': constants.LIST,
        'create': constants.CREATE,
        'retrieve': constants.VIEW,
        'update': constants.EDIT,
        'partial_update': constants.EDIT,
        'destroy': constants.DELETE,
        'metadata': constants.VIEW,
    }

    return action_map.get(action, action)
