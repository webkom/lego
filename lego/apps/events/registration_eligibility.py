from dataclasses import dataclass
import json
from datetime import datetime

from lego.apps.events.constants import RegistrationEligibilityReason


@dataclass
class RegistrationEligibility:
    is_registration_delayed: bool | None = False
    earliest_registration_time: datetime | None = None
    will_be_waiting_list: bool | None = False
    reason: RegistrationEligibilityReason | None = None
    registration_disallowed: bool | None = False

    def to_dict(self) -> dict:
            return {
                "is_registration_delayed": self.is_registration_delayed,
                "earliest_registration_time": (
                    self.earliest_registration_time.isoformat()
                    if self.earliest_registration_time
                    else None
                ),
                "will_be_waiting_list": self.will_be_waiting_list,
                "reason": str(self.reason) if self.reason else None,
                "registration_disallowed": self.registration_disallowed,
            }
    
    @classmethod
    def from_dict(cls, data: dict) -> "RegistrationEligibility":
        earliest = data.get("earliest_registration_time")
        reason = data.get("reason")
        return cls(
            is_registration_delayed=data.get("is_registration_delayed"),
            earliest_registration_time=(
                datetime.fromisoformat(earliest) if earliest else None
            ),
            will_be_waiting_list=data.get("will_be_waiting_list"),
            reason=RegistrationEligibilityReason(reason) if reason else None,
            registration_disallowed=data.get("registration_disallowed"),
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, raw: str) -> "RegistrationEligibility":
        return cls.from_dict(json.loads(raw))