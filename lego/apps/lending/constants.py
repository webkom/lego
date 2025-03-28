from datetime import date
from typing import Optional, TypedDict

LENDING_REQUEST_STATUSES = {
    "LENDING_UNAPPROVED": {"value": "unapproved"},
    "LENDING_APPROVED": {"value": "approved"},
    "LENDING_DENIED": {"value": "denied"},
    "LENDING_CANCELLED": {"value": "cancelled"},
    "LENDING_CHANGES_REQUESTED": {"value": "changes_requested"},
}

LENDING_REQUEST_DEFAULT = LENDING_REQUEST_STATUSES["LENDING_UNAPPROVED"]["value"]

LENDING_CHOICE_STATUSES = sorted(
    {(value["value"], value["value"]) for value in LENDING_REQUEST_STATUSES.values()}
)

LENDING_REQUEST_TRANSLATION_MAP = {
    "unapproved": "Ikke godkjent",
    "approved": "Godkjent",
    "denied": "Avslått",
    "cancelled": "Avbrutt av bruker",
    "changes_requested": "Endringer forespurt",
}


class CreateLendingRequestType(TypedDict):
    id: int
    created_by: Optional[int]  # Assuming user IDs are integers
    updated_by: Optional[int]
    lendable_object: int  # Assuming this is a foreign key ID
    status: str
    text: str
    start_date: date
    end_date: date
    comments: list
