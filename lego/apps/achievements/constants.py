from .verification import (
    check_event_generic,
    check_event_price_over,
    check_event_rank,
    check_poll_responses,
    check_verified_quote,
)

EVENT_IDENTIFIER = "event_count"
EVENT_RANK_IDENTIFIER = "event_rank"
EVENT_PRICE_IDENTIFIER = "event_price"
QUOTE_IDENTIFIER = "quote_count"
MEETING_IDENTIFIER = "meeting_hidden"
POLL_IDENTIFIER = "poll_count"

EVENT_ACHIEVEMENTS = {
    "arrangement_10": {
        "identifier": EVENT_IDENTIFIER,
        "requirement_function": lambda user: check_event_generic(user=user, count=10),
        "hidden": False,
        "level": 0,
    },
    "arrangement_25": {
        "identifier": EVENT_IDENTIFIER,
        "requirement_function": lambda user: check_event_generic(user=user, count=25),
        "hidden": False,
        "level": 1,
    },
    "arrangement_50": {
        "identifier": EVENT_IDENTIFIER,
        "requirement_function": lambda user: check_event_generic(user=user, count=50),
        "hidden": False,
        "level": 2,
    },
    "arrangement_100": {
        "identifier": EVENT_IDENTIFIER,
        "requirement_function": lambda user: check_event_generic(user=user, count=100),
        "hidden": False,
        "level": 3,
    },
    "arrangement_150": {
        "identifier": EVENT_IDENTIFIER,
        "requirement_function": lambda user: check_event_generic(user=user, count=150),
        "hidden": False,
        "level": 4,
    },
}

# requirementFunction is not used for rank achievements.
# Handled globally in promotion script
EVENT_RANK_ACHIEVEMENTS = {
    "event_rank_3": {
        "identifier": EVENT_RANK_IDENTIFIER,
        "requirement_function": lambda user: check_event_rank(user=user, rank=3),
        "hidden": False,
        "level": 0,
    },
    "event_rank_2": {
        "identifier": EVENT_RANK_IDENTIFIER,
        "requirement_function": lambda user: check_event_rank(user=user, rank=2),
        "hidden": False,
        "level": 1,
    },
    "event_rank_1": {
        "identifier": EVENT_RANK_IDENTIFIER,
        "requirement_function": lambda user: check_event_rank(user=user, rank=1),
        "hidden": False,
        "level": 2,
    },
}

QUOTE_ACHIEVEMENTS = {
    "quote_1": {
        "identifier": QUOTE_IDENTIFIER,
        "requirement_function": lambda user: check_verified_quote(user=user),
        "hidden": True,
        "level": 0,
    },
}

EVENT_PRICE_ACHIEVEMENTS = {
    "price_1": {
        "identifier": EVENT_PRICE_IDENTIFIER,
        "requirement_function": lambda user: check_event_price_over(
            user=user, price=250000
        ),
        "hidden": False,
        "level": 0,
    },
    "price_2": {
        "identifier": EVENT_PRICE_IDENTIFIER,
        "requirement_function": lambda user: check_event_price_over(
            user=user, price=500000
        ),
        "hidden": False,
        "level": 1,
    },
    "price_3": {
        "identifier": EVENT_PRICE_IDENTIFIER,
        "requirement_function": lambda user: check_event_price_over(
            user=user, price=1000000
        ),
        "hidden": False,
        "level": 2,
    },
}

MEETING_ACHIEVEMENTS = {
    "meeting_hidden": {
        "identifier": MEETING_IDENTIFIER,
        "requirement_function": lambda user: False,
        "hidden": True,
        "level": 0,
    },
}

POLL_ACHIEVEMENTS = {
    "poll_5": {
        "identifier": POLL_IDENTIFIER,
        "requirement_function": lambda user: check_poll_responses(user=user, count=5),
        "hidden": False,
        "level": 0,
    },
    "poll_25": {
        "identifier": POLL_IDENTIFIER,
        "requirement_function": lambda user: check_poll_responses(user=user, count=25),
        "hidden": False,
        "level": 1,
    },
    "poll_50": {
        "identifier": POLL_IDENTIFIER,
        "requirement_function": lambda user: check_poll_responses(user=user, count=50),
        "hidden": False,
        "level": 2,
    },
}


HIDDEN_ACHIEVEMENTS = {**QUOTE_ACHIEVEMENTS, **MEETING_ACHIEVEMENTS}


ACHIEVEMENTS = {
    **EVENT_ACHIEVEMENTS,
    **EVENT_RANK_ACHIEVEMENTS,
    **EVENT_PRICE_ACHIEVEMENTS,
    **POLL_ACHIEVEMENTS,
    **HIDDEN_ACHIEVEMENTS,
}


ACHIEVEMENT_IDENTIFIERS = [
    (value["identifier"], value["identifier"]) for value in ACHIEVEMENTS.values()
]
