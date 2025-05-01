from datetime import timedelta

SITE = {
    "name": "LEGO",
    "slogan": "LEGO Er Ganske Oppdelt",
    "contact_email": "webkom@abakus.no",
    "documentation_url": "/docs/",
    "domain": "abakus.no",
    "owner": "Abakus",
}

API_VERSION = "v1"
LOGIN_REDIRECT_URL = f"/api/{API_VERSION}/"

EMAIL_SUBJECT_PREFIX = "[Abakus] "

ADMINS = (("Webkom", "webkom@abakus.no"),)
MANAGERS = ADMINS

PENALTY_DURATION = timedelta(days=20)
# Tuples for ignored (month, day) intervals
PENALTY_IGNORE_SUMMER = ((6, 1), (8, 15))
PENALTY_IGNORE_WINTER = ((11, 18), (1, 10))

BEDKOM_BOOKING_PERIOD = ((1, 1), (12, 30))

REGISTRATION_CONFIRMATION_TIMEOUT = 60 * 60 * 24

PASSWORD_RESET_TIMEOUT = 60 * 60 * 24

HEALTH_CHECK_REMOTE_IPS = ["10.", "127.0.0."]

LDAP_GROUPS = [
    "Ababand",
    "Fondsstyret",
    "Abakus-leder",
    "Hovedstyret",
    "Komiteledere",
    "itDAGENE",
    "Jubileum",
    "Kasserere",
    "Ordenen",
    "PR-ansvarlige",
    "Revy",
    "RevyStyret",
    "xcom-data",
    "xcom-komtek",
    "Nestledere",
    "HS-representant",
]

SMTP_HOST = "0.0.0.0"
SMTP_PORT = 8025

RESTRICTED_ADDRESS = "restricted"
RESTRICTED_DOMAIN = "abakus.no"
RESTRICTED_FROM = "Abakus <no-reply@abakus.no>"
RESTRICTED_ALLOW_ORIGINAL_SENDER = False

GSUITE_DOMAIN = "abakus.no"

GSUITE_GROUPS = []

#  External users in GSuite not managed by lego. (Don't suspend these.)
GSUITE_EXTERNAL_USERS = ["admin@abakus.no", "noreply@abakus.no", "sofaktura@abakus.no"]
