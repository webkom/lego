from django.core.validators import RegexValidator

youtube_validator = RegexValidator(
    regex=(r"(^(?:https?:\/\/)?(?:www[.])?(?:youtube[.]com\/watch[?]v=|youtu[.]be\/))")
)
