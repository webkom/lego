from django.conf import settings
from django.shortcuts import resolve_url

from .models import File
from .storage import storage
from .tokens import RedirectTokenGenerator

token_generator = RedirectTokenGenerator()


def create_redirect_token(file):
    """
    Create a token used on update success requests.
    """
    return token_generator.make_token(file)


def validate_redirect_token(file, token):
    """
    Validate tokens attached to upload success requests.
    """
    if token:
        return token_generator.check_token(file, token)

    return False


def prepare_file_upload(key):
    """
    Create instructions for the client on how to upload a new file. This functions returns two
    values, the first one is the url the file should be uploaded to and the secound value is a
    dict with additional fields the client need to attach to the upload request.
    """
    file = File.create_file(key)
    token = create_redirect_token(file)
    redirect_url = '{0}{1}?token={2}'.format(
        settings.SERVER_URL,
        resolve_url('api:v1:file-upload-success', file.key),
        token
    )
    signed_post = storage.generate_upload_url(file.bucket, file.key, redirect_url)

    return signed_post['url'], signed_post['fields']
