import os

import boto3
from botocore import exceptions
from django.conf import settings
from django.core.exceptions import SuspiciousFileOperation
from django.utils.crypto import get_random_string


class Storage:

    def __init__(self):
        self.session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        self.client = self.session.client('s3')
        self.resource = self.session.resource('s3')

    def generate_upload_url(self, bucket, key, redirect_url):
        signed = self.client.generate_presigned_post(
            Bucket=bucket,
            Key=key,
            Conditions=[
                ['content-length-range', 10, '1000000000'],
                {'success_action_redirect': redirect_url},
                {'acl': 'private'}
            ],
            Fields={
                'success_action_redirect': redirect_url,
                'acl': 'private'
            },
            ExpiresIn=30
        )
        return signed

    def generate_signed_url(self, bucket, key):
        params = {
            'Bucket': bucket,
            'Key': key
        }
        presigned_url = self.client.generate_presigned_url(
            ClientMethod='get_object', Params=params, ExpiresIn=60
        )
        return presigned_url

    def key_exists(self, bucket, key):
        try:
            self.resource.Object(bucket, key).load()
            return True
        except exceptions.ClientError:
            pass

        return False

    def get_available_name(self, bucket, key, max_length=32, force_name_change=False):
        file_root, file_ext = os.path.splitext(key)
        while force_name_change or self.key_exists(bucket, key) or \
                (max_length and len(key) > max_length):
            force_name_change = False
            # file_ext includes the dot.
            key = "%s_%s%s" % (file_root, get_random_string(7), file_ext)
            if max_length is None:
                continue
            # Truncate file_root if max_length exceeded.
            truncation = len(key) - max_length
            if truncation > 0:
                file_root = file_root[:-truncation]
                # Entire file_root was truncated in attempt to find an available filename.
                if not file_root:
                    raise SuspiciousFileOperation(
                        'Storage can not find an available filename for "%s". '
                        'Please make sure that the corresponding file field '
                        'allows sufficient "max_length".' % key
                    )
                key = "%s_%s%s" % (file_root, get_random_string(7), file_ext)
        return key


storage = Storage()
