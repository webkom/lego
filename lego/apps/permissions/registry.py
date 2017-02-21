

permission_registry = {}


def register_permission_index(permission_index_cls):
    from lego.utils.content_types import instance_to_content_type_string

    permission_index = permission_index_cls()
    model = permission_index.get_model()
    permission_registry[instance_to_content_type_string(model)] = permission_index


def parse_permission_string(perm):
    from lego.utils.content_types import action_string_to_content_type_and_action
    content_type, action = action_string_to_content_type_and_action(perm)
    return getattr(permission_registry.get(content_type), action, None)


def get_permission_string(instance, action):
    from lego.utils.content_types import instance_to_content_type_action_string
    return instance_to_content_type_action_string(instance, action)
