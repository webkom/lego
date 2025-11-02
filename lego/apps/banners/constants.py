BANNER_COLORS = {
    "RED": {"value": "red"},
    "WHITE": {"value": "white"},
    "GRAY": {"value": "gray"},
    "LIGHT_BLUE": {"value": "lightBlue"},
    "ITDAGENE_BLUE": {"value": "itdageneBlue"},
    "BUDDYWEEK": {"value": "buddyweek2024"},
    "EASTER": {"value": "easter"},
    "CHRISTMAS": {"value": "christmas"}
}

BANNER_COLORS_DEFAULT = BANNER_COLORS["RED"]["value"]

BANNER_COLORS_CHOICES = sorted(
    {(value["value"], value["value"]) for value in BANNER_COLORS.values()}
)
