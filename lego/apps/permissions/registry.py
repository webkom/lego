

permission_registry = {}


def register_permission_index(permission_index_cls):
    from lego.utils.content_types import instance_to_content_type_string

    permission_index = permission_index_cls()
    model = permission_index.get_model()
    permission_registry[instance_to_content_type_string(model)] = permission_index


def parse_permission_string(perm):
    """
    Parses permission strings on the format <app_label>.<model>.<action>
    E.g. "events.event.list" into permission_tuple of ([keyword_permissions], safe_method)
    :param perm: String on format: <app_label>.<model>.<action>
    :return: Permission tuple ([<keyword_permissions>], safe_method) or None
    """
    content_type, action = perm.rsplit('.', 1)
    permission_content = permission_registry.get(content_type)
    keyword = getattr(permission_content, action, None)
    safe_method = action in getattr(permission_content, 'safe_methods', False)
    if keyword is None:
        return None
    return keyword, safe_method


def get_permission_string(instance, action):
    """
    Generate permission string based on instance and action.
    :param instance: Object, e.g. Event.object.get(pk=1)
    :param action: Action, e.g. 'list', 'retrieve' or 'destroy'
    :return: Permission string on the format <app_label>.<model>.<action>, e.g. events.event.list
    """
    from lego.utils.content_types import instance_to_content_type_action_string
    return instance_to_content_type_action_string(instance, action)
