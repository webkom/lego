from django.db import models

from lego.apps.tags.validators import validate_tag


class Tag(models.Model):
    tag = models.CharField(max_length=64, primary_key=True, validators=[validate_tag])

    def related_counts(self):
        related_fields = [relation.name for relation in self._meta.related_objects]
        return {
            related_field: getattr(self, f'{related_field}_count', 0)
            for related_field in related_fields
        }
