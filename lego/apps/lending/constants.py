from datetime import date
from typing import Optional, TypedDict

LENDING_REQUEST_STATUSES = {
    "LENDING_CREATED": {"value": "created"},
    "LENDING_UNAPPROVED": {"value": "unapproved"},
    "LENDING_APPROVED": {"value": "approved"},
    "LENDING_DENIED": {"value": "denied"},
    "LENDING_CANCELLED": {"value": "cancelled"},
    "LENDING_CHANGES_REQUESTED": {"value": "changes_requested"},
    "LENDING_CHANGES_RESOLVED": {"value": "changes_resolved"},
}

OUTDOORS = "outdoors"
PHOTOGRAPHY = "photography"
MUSIC = "music"
FURNITURE = "furniture"
SERVICES = "services"
OTHER = "other"

LENDING_CATEGORIES = (
    (OUTDOORS, OUTDOORS),
    (PHOTOGRAPHY, PHOTOGRAPHY),
    (MUSIC, MUSIC),
    (FURNITURE, FURNITURE),
    (SERVICES, SERVICES),
    (OTHER, OTHER),
)

LENDING_REQUEST_DEFAULT = LENDING_REQUEST_STATUSES["LENDING_UNAPPROVED"]["value"]

LENDING_CHOICE_STATUSES = sorted(
    {(value["value"], value["value"]) for value in LENDING_REQUEST_STATUSES.values()}
)

LENDING_REQUEST_TRANSLATION_MAP = {
    "created": "opprettet forespørsel",
    "unapproved": "fjernet godkjenning",
    "approved": "godkjente forespørsel",
    "denied": "avslo forespørsel",
    "cancelled": "avbrøt forespørsel",
    "changes_requested": "forespurte endringer",
    "changes_resolved": "løste endringer",
}


LENDING_REQUEST_USER_ACTIONS = [
    LENDING_REQUEST_STATUSES["LENDING_CANCELLED"]["value"],
    LENDING_REQUEST_STATUSES["LENDING_CHANGES_RESOLVED"]["value"],
]

LENDING_REQUEST_ADMIN_ACTIONS = [
    LENDING_REQUEST_STATUSES["LENDING_APPROVED"]["value"],
    LENDING_REQUEST_STATUSES["LENDING_DENIED"]["value"],
    LENDING_REQUEST_STATUSES["LENDING_CHANGES_REQUESTED"]["value"],
]


class CreateLendingRequestType(TypedDict):
    id: int
    created_by: Optional[int]  # Assuming user IDs are integers
    updated_by: Optional[int]
    lendable_object: int  # Assuming this is a foreign key ID
    status: str
    comment: str
    start_date: date
    end_date: date
    comments: list
