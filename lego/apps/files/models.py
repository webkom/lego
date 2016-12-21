from datetime import timedelta

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone
from structlog import get_logger

from lego.utils.models import TimeStampModel

from .constants import FILE_STATES, PENDING_UPLOAD, READY
from .storage import storage
from .validators import key_validator

log = get_logger()


class File(TimeStampModel):
    key = models.CharField(max_length=200, validators=[key_validator], primary_key=True)
    state = models.CharField(max_length=24, choices=FILE_STATES, default=PENDING_UPLOAD)

    bucket = settings.AWS_S3_BUCKET

    def upload_done(self):
        if self.exist_on_remote():
            self.state = READY
            self.save()

    def exist_on_remote(self):
        return storage.key_exists(self.bucket, self.key)

    @classmethod
    def create_file(cls, key):
        with transaction.atomic():
            token_exists = cls.objects.filter(key=key).exists()
            key = storage.get_available_name(cls.bucket, key, force_name_change=token_exists)
            return cls.objects.create(key=key)

    @classmethod
    def purge_garbage(cls):
        """
        Purge stale files from DB.
        """
        stale_threshold = timezone.now() - timedelta(hours=12)
        garbage = cls.objects.filter(state=PENDING_UPLOAD, created_at__lte=stale_threshold)
        result = garbage.delete()
        log.info('noetikon_file_purge_garbage', row_count=result[1])


class FileField(models.ForeignKey):
    """
    FileField with reasonable defaults.
    """

    def __init__(self, **kwargs):
        kwargs['to'] = 'files.File'
        kwargs['on_delete'] = models.SET_NULL
        kwargs['null'] = True
        super().__init__(**kwargs)
