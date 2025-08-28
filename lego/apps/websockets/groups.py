from __future__ import annotations

from typing import TYPE_CHECKING

from lego.apps.permissions.constants import LIST
from lego.apps.users.models import User
from lego.utils.content_types import instance_to_string, string_to_instance

if TYPE_CHECKING:
    from lego.apps.events.models import Event


def group_for_user(user_id: str) -> str:
    return f"user-{user_id}"


def group_for_event(event: Event, has_registrations_access: bool) -> str:
    return f"event-{'full' if has_registrations_access else 'limited'}-{event.pk}"


def group_for_content_model(model) -> str:
    modelname = model._meta.model_name
    content_target_string = instance_to_string(model.content_object)
    return f"{modelname}-{content_target_string}"


def verify_group_access(user: User, group):
    if not group:
        return False

    group_type, rest = group.split("-", 1)

    if group_type == "comment":
        content_target = string_to_instance(rest)
        if user and content_target:
            return user.has_perm(LIST, content_target)

    # if group_type == WS_GROUP_TYPE_USER:
    #     user_id = rest
    #     return user_id == str(user.pk)

    # if group_type == WS_GROUP_TYPE_EVENT:
    #     event_access, event_id = rest.split("-", 1)
    #     """Not implemented"""

    return False


def stringify_group(group):
    pass

    # if content_target:
    #     return f"{group.type}-{content_target}"

    # return str(group.type)
