from dataclasses import dataclass
from datetime import datetime


@dataclass
class RegistrationEligibility:
    can_register_now: bool
    reason: str | None  # e.g. "already_registered", "registration_closed", ...
    is_registration_delayed: bool | None = None
    delay_until: datetime | None = None
    delay_seconds: int | None = None
    will_be_waiting_list: bool | None = None
