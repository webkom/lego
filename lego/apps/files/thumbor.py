from django.conf import settings

from libthumbor import CryptoURL
from structlog import get_logger

log = get_logger()
log = log.bind()

THUMBOR_SERVER = getattr(settings, "THUMBOR_SERVER", "http://localhost:8888").rstrip(
    "/"
)
THUMBOR_SECURITY_KEY = getattr(settings, "THUMBOR_SECURITY_KEY", "MY_SECURE_KEY")

crypto = CryptoURL(key=THUMBOR_SECURITY_KEY)


# Deny empty or none url
def _handle_empty(url):
    if not url:
        log.error("empty_url")
        return ""
    return url


# Accept string url and ImageField or similar classes
# with "url" attr as param
def _handle_url_field(url):
    if hasattr(url, "url"):
        return getattr(url, "url", "")
    return url


def generate_url(image_url, **kwargs):
    image_url = _handle_empty(image_url)
    image_url = _handle_url_field(image_url)

    thumbor_server = kwargs.pop("thumbor_server", THUMBOR_SERVER).rstrip("/")
    encrypted_url = crypto.generate(image_url=image_url, **kwargs).strip("/")

    return "%s/%s" % (thumbor_server, encrypted_url)
