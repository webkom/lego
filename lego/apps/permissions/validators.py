from django.core.validators import RegexValidator


class KeywordPermissionValidator(RegexValidator):
    regex = r'^/([a-zA-Z]+/)+$'
    message = 'Keyword permissions can only contain forward slashes and letters ' \
              'and must begin and end with a forward slash'
