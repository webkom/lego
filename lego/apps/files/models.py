from datetime import timedelta
from mimetypes import guess_type

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone
from django.utils.crypto import get_random_string
from structlog import get_logger, threadlocal

from lego.apps.files.exceptions import UnknownFileType
from lego.utils.models import TimeStampModel

from .constants import DOCUMENT, FILE_STATES, FILE_TYPES, IMAGE, PENDING_UPLOAD, READY
from .storage import storage
from .validators import key_validator

log = get_logger()


class File(TimeStampModel):
    key = models.CharField(max_length=200, validators=[key_validator], primary_key=True)
    state = models.CharField(max_length=24, choices=FILE_STATES, default=PENDING_UPLOAD)
    file_type = models.CharField(max_length=24, choices=FILE_TYPES)
    token = models.CharField(max_length=32)
    user = models.ForeignKey('users.User', related_name='uploaded_files', null=True)
    bucket = getattr(settings, 'AWS_S3_BUCKET', None)
    public = models.BooleanField(default=False, null=False)

    def upload_done(self):
        with threadlocal.tmp_bind(log, file=self.key) as tmp_log:
            if self.exist_on_remote():
                self.state = READY
                self.save()
                tmp_log.info('file_upload_state_success')
            else:
                tmp_log.warn('file_upload_state_failure', reason='not_on_remote')

    def exist_on_remote(self):
        return storage.key_exists(self.bucket, self.key)

    @classmethod
    def create_file(cls, key, user, public):
        with transaction.atomic():
            key_exists = cls.objects.filter(key=key).exists()
            key_storage_name = storage.get_available_name(
                cls.bucket, key, force_name_change=key_exists
            )
            file_token = get_random_string(32)
            file = cls.objects.create(
                key=key_storage_name,
                file_type=cls.get_file_type(key_storage_name),
                token=file_token,
                user=user,
                public=public
            )
            log.info('file_upload_new', user_key=key, file=key_storage_name)
            return file

    @classmethod
    def purge_garbage(cls):
        """
        Purge stale files from DB.
        """
        stale_threshold = timezone.now() - timedelta(hours=12)
        garbage = cls.objects.filter(state=PENDING_UPLOAD, created_at__lte=stale_threshold)
        result = garbage.delete()
        log.info(
            'file_purge_garbage', row_count=result[1], stale_threshold=stale_threshold
        )

    @classmethod
    def get_file_type(cls, file_name):
        """
        Extract file type from a file name.
        """
        mime_type, encoding = guess_type(file_name)
        known_mime_types = {
            'image/jpeg': IMAGE,
            'image/png': IMAGE,
            'application/pdf': DOCUMENT
        }

        try:
            return known_mime_types[mime_type]
        except KeyError:
            log.warn('file_unknown_type', file_name=file_name, mime_type=mime_type)
            raise UnknownFileType

    def get_file_token(self):
        return f'{self.key}:{self.token}'


class FileField(models.ForeignKey):
    """
    FileField with reasonable defaults.
    """

    def __init__(self, **kwargs):
        kwargs['to'] = 'files.File'
        kwargs['on_delete'] = models.SET_NULL
        kwargs['null'] = True
        super().__init__(**kwargs)
