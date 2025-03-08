from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from lego.utils.models import BasisModel


class FeatureFlag(BasisModel):
    identifier = models.CharField(max_length=255, unique=True, null=False, blank=False)
    is_active = models.BooleanField(default=False, null=False)
    percentage = models.PositiveIntegerField(
        default=None,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    display_groups = models.ManyToManyField(
        "users.AbakusGroup",
        blank=True,
    )

    def can_see_flag(self, user=None):
        """
        Determines if a user should see the feature flag based on:
        - Active status (`is_active`)
        - Random selection (`percentage`)
        - Group membership (`display_groups`)
        """
        if not self.is_active:
            return False

        # Check if user is within the percentage threshold
        if self.percentage is not None:
            if user is None:
                return False
            if not self._deterministic_selection(user.id, self.percentage):
                return False

        # If display_groups is set, ensure the user belongs to at least one of them
        if self.display_groups.exists():
            if user is None:
                return False
            if not user.memberships.filter(
                abakus_group__in=self.display_groups.all(), is_active=True
            ).exists():
                return False

        return True

    @staticmethod
    def _deterministic_selection(user_id, percentage):
        """
        Determines if a user ID should be selected based on a given percentage.
        Uses a lightweight hash-like function for even distribution.
        """
        hash_value = (user_id * 2654435761) & 0xFFFFFFFF
        return (hash_value % 100) < percentage

    def delete(self, using=None, force=True):
        return super().delete(using, force)
