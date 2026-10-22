import json
from datetime import datetime
from typing import Any
from django.core.cache import cache
from django.utils import timezone
from lego.apps.events.models import Event, RegistrationEligibility
from lego.apps.users.models import User


class RegistrationEligibilityCache:
  KEY_PREFIX = "event_eligibility"
  DEFAULT_TTL = 3600 # 60 minutes / 1 Hour

  @classmethod
  def make_key(cls, event_id: int, user_id: int) -> str:
    return f"{cls.KEY_PREFIX}:{event_id}:{user_id}"

  @classmethod
  def get(cls, event: Event, user: User) -> dict[str, Any]:
    """"""
    key = cls.make_key(event.id, user.id)
    cached = cache.get(key)

    print("==========================================GETTING CACHE ENTRY=======================================")

    if cached:
      data = RegistrationEligibility.from_json(cached)
    #   earliest = datetime.fromisoformat(data["earliest_registration_time"])
    #   data["can_register_now"] = not data["is_blocked"] and timezone.now() >= earliest
      return data

    # Cache miss case
    eval_result = event.evaluate_registration_eligibility(user=user)

    # TODO: Fix registration eligibility result serialization 
    cache.set(key, eval_result.to_json(), timeout=cls.DEFAULT_TTL)

    return eval_result

  @classmethod
  def invalidate_user(cls, user_id: int) -> None:
    cache.delete_pattern(f"{cls.KEY_PREFIX}:*:{user_id}")

  @classmethod
  def invalidate_event(cls, event_id: int) -> None:
    cache.delete_pattern(f"{cls.KEY_PREFIX}:{event_id}:*")

