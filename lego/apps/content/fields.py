from django.core.exceptions import ValidationError
from django.db.models import TextField
from rest_framework import serializers

from bs4 import BeautifulSoup
from structlog import get_logger

from lego.apps.content.utils import sanitize_html
from lego.apps.files.constants import IMAGE, READY
from lego.apps.files.models import File
from lego.apps.files.thumbor import generate_url

log = get_logger()


class ContentField(TextField):
    """
    Model field with a html sanitizer.
    """

    description = "TextField with a html sanitizer"

    def __init__(self, allow_images=False, *args, **kwargs):
        self.allow_images = allow_images
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        # Only include kwarg if it's not the default
        if not self.allow_images:
            kwargs["allow_images"] = self.allow_images
        return name, path, args, kwargs

    def to_python(self, value):
        """
        Sanitize html and make sure linked images is accessible.
        """
        value = super().to_python(value)
        if value is None:
            return value

        safe_value = sanitize_html(value, allow_images=self.allow_images)

        images = []
        html = BeautifulSoup(safe_value, "html.parser")
        for image in html.find_all("img"):
            if not self.allow_images:
                raise ValidationError("img tags not allowed")

            data_key = image.get("data-file-key")
            if data_key is not None:
                images.append(data_key)
            else:
                log.warn(
                    f"Found img tag without the data-file-key property in ContentField with value: {value}"
                )

        if images:
            files = File.objects.filter(
                key__in=images, public=True, state=READY, file_type=IMAGE
            )
            diff = set(images) - {file.key for file in files}
            if len(diff):
                raise ValidationError(f"Images {diff} not found")

        return str(html)


class ContentSerializerField(serializers.CharField):
    """
    Serializer field with thumbor url injection.
    """

    def to_representation(self, value):
        safe_value = sanitize_html(value, allow_images=True)

        html = BeautifulSoup(safe_value, "html.parser")
        for image in html.find_all("img"):
            image["src"] = generate_url(image.get("data-file-key"))
        return str(html)
