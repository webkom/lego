from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lego.apps.events.models import Event


def group_for_user(user_id: str) -> str:
    return f"user-{user_id}"


def group_for_event(event: Event, has_registrations_access: bool) -> str:
    return f"event-{'full' if has_registrations_access else 'limited'}-{event.pk}"
