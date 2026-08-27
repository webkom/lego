from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):
    """
    Enable the pg_trgm extension, used by search autocomplete for typo tolerant
    (trigram similarity) matching.

    NB: On PostgreSQL < 13 this requires a superuser. On 13+ pg_trgm is a trusted
    extension and the database owner is enough.
    """

    dependencies = []

    operations = [TrigramExtension()]
