LENDING_REQUEST_STATUSES = {
    "LENDING_UNAPPROVED": {"value": "lending_unapproved"},
    "LENDING_APPROVED": {"value": "lending_approved"},
    "LENDING_DENIED": {"value": "lending_denied"},
    "LENDING_CHANGES_REQUESTED": {"value": "lending_changes_requested"},
}

LENDING_REQUEST_DEFAULT = (
    LENDING_REQUEST_STATUSES["LENDING_UNAPPROVED"]["value"],
    LENDING_REQUEST_STATUSES["LENDING_UNAPPROVED"]["value"],
)

LENDING_CHOICE_STATUSES = sorted(
    {(value["value"], value["value"]) for value in LENDING_REQUEST_STATUSES.values()}
)
