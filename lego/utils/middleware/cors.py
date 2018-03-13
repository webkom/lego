import re

from django.utils.deprecation import MiddlewareMixin

from lego.apps.files.validators import KEY_REGEX_RAW


class CORSPatchMiddleware(MiddlewareMixin):
    """
    The cors header seems to break the file upload endpoint when using firefox.
    This is a temporarily patch to fix this.
    """

    header = 'Access-Control-Allow-Origin'
    regex_path = f'/api/v1/files/{KEY_REGEX_RAW}/upload_success/'
    regex = re.compile(regex_path)

    def process_response(self, request, response):
        if self.regex.match(request.path):
            response[self.header] = '*'
        return response
