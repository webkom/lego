import os
from mimetypes import guess_type

import boto3
from botocore import exceptions
from django.conf import settings
from django.core.exceptions import SuspiciousFileOperation
from django.utils.crypto import get_random_string


class Storage:

    def __init__(self):
        self.session = boto3.Session(
            aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', None),
            aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None),
            region_name=getattr(settings, 'AWS_REGION', None),
        )
        self.client = self.session.client(
            's3', endpoint_url=getattr(settings, 'AWS_ENTRYPOINT', None)
        )
        self.resource = self.session.resource(
            's3', endpoint_url=getattr(settings, 'AWS_ENTRYPOINT', None)
        )

    def generate_upload_url(self, bucket, key, redirect_url):
        mime_type, encoding = guess_type(key)

        signed = self.client.generate_presigned_post(
            Bucket=bucket,
            Key=key,
            Conditions=[
                ['content-length-range', 10, 1000000000],
                {'success_action_redirect': redirect_url},
                {'acl': 'private'},
                {'Content-Type': mime_type}
            ],
            Fields={
                'success_action_redirect': redirect_url,
                'acl': 'private',
                'Content-Type': mime_type
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

    def create_bucket(self, bucket, acl='private'):
        """
        Create a bucket
        """
        try:
            bucket = self.resource.Bucket(bucket)
            bucket.create(ACL=acl)
            return bucket
        except exceptions.ClientError:
            pass

    def add_bucket_event(self, bucket, event_type, event_configuration):
        """
        Add a notification type on a given bucket
        """
        try:
            if event_type == 'webhook':
                bucket_notification = self.resource.BucketNotification(bucket)
                bucket_notification.put(NotificationConfiguration={
                    'LambdaFunctionConfigurations': [event_configuration]
                })
            elif event_type == 'queue':
                bucket_notification = self.resource.BucketNotification(bucket)
                bucket_notification.put(NotificationConfiguration={
                    'QueueConfigurations': [event_configuration]
                })
            elif event_type == 'topic':
                pass
            else:
                raise ValueError(
                    f'Paramter {event_type} invalid, must be one of: webhook, queue, topic'
                )
        except exceptions.ClientError:
            pass

    def upload_file(self, bucket, key, file_name):
        """
        Upload a file to S3 using the filename as the path to the file on the local filesystem
        """
        try:
            self.client.upload_file(file_name, bucket, key)
        except exceptions.ClientError:
            pass


storage = Storage()
