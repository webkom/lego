from __future__ import annotations

from typing import TYPE_CHECKING

from lego.utils.content_types import instance_to_string

if TYPE_CHECKING:
    from lego.apps.events.models import Event


def group_for_user(user_id: str) -> str:
    return f"user-{user_id}"


def group_for_event(event: Event, has_registrations_access: bool) -> str:
    return f"event-{'full' if has_registrations_access else 'limited'}-{event.pk}"


def group_for_content_target(content_target) -> str:
    content_target_string = instance_to_string(content_target)
    return f"comment-{content_target_string}"
