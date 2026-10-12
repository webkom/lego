from dataclasses import dataclass
from datetime import datetime

from lego.apps.events.constants import RegistrationEligibilityReason


@dataclass
class RegistrationEligibility:
    can_register_now: bool
    can_register_later: bool | None = None
    reason: RegistrationEligibilityReason | None = None
    is_registration_delayed: bool | None = None
    delay_until: datetime | None = None
    will_be_waiting_list: bool | None = None
