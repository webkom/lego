from django.conf import settings
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

VALID_COMMAND_IDS = {
    "home",
    "profile",
    "events",
    "meetings",
    "lending",
    "interestGroups",
    "joblistings",
    "companies",
    "articles",
    "gallery",
    "quotes",
    "trophies",
    "theFund",
    "developerBlog",
    "settings",
    "createMeetingNotice",
    "createReceipt",
    "createQuote",
    "createAlbum",
    "logout",
}


def validate_command_id(value: str):
    """
    Validate command_id in whitelist
    """
    if value not in VALID_COMMAND_IDS:
        raise ValidationError(f"Invalid command_id: {value!r}")


username_validator = validators.RegexValidator(
    r"^[a-zA-Z0-9_]+$",
    "Enter a valid username. This value may contain only letters, numbers and _ "
    "characters.",
    "invalid",
)

STUDENT_USERNAME_REGEX = r"[a-zA-Z0-9_\.]+"

student_username_validator = validators.RegexValidator(
    rf"^{STUDENT_USERNAME_REGEX}$",
    "Enter a valid username. This value may contain only letters, numbers, _ and . "
    "characters.",
    "invalid",
)

github_username_validator = validators.RegexValidator(
    r"^[a-zA-Z\d](?:[a-zA-Z\d]|-(?=[a-zA-Z\d])){0,38}$",
    "Enter a valid GitHub username.",
)

linkedin_id_validator = validators.RegexValidator(
    r"^[a-zA-Z0-9-]{0,70}$",
    "Enter a valid LinkedIn ID.",
)


@deconstructible
class EmailValidatorWithBlacklist:
    """
    Takes a blacklist argument and raises an ValueError if the domainpart of the address exists
    in the blacklist.
    """

    code = "invalid"
    domain_blacklist = []

    def __init__(self, blacklist=None, *args, **kwargs):
        if blacklist is not None:
            self.domain_blacklist = blacklist

    def __call__(self, value):
        try:
            _, domain_part = value.rsplit("@", 1)
        except ValueError as e:
            raise ValidationError("Invalid email", code=self.code) from e

        if domain_part.lower() in self.domain_blacklist:
            message = "You can't use a {} email for your personal account.".format(
                domain_part
            )
            raise ValidationError(message, code=self.code)

    def __eq__(self, other):
        return self.domain_blacklist == other.domain_blacklist and super().__eq__(other)


# We do not permit emails from our GSuite account - causes circular dependencies.
email_blacklist_validator = EmailValidatorWithBlacklist(
    blacklist=[settings.GSUITE_DOMAIN]
)
