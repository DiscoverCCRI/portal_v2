from datetime import datetime

from django.db import models

from portal.apps.mixins.models import BaseModel, BaseTimestampModel

# constants
MAX_CANONICAL_NUMBER = 9999

# global for Canonical Number
current_canonical_number = 0


def get_current_canonical_number() -> int:
    global current_canonical_number
    if CanonicalNumber.objects.filter(canonical_number=current_canonical_number, is_deleted=False).exists() or \
            int(current_canonical_number) < 1 or int(current_canonical_number) > 9999:
        return increment_current_canonical_number()
    return current_canonical_number


def set_current_canonical_number(new_number: int = None) -> int:
    global current_canonical_number
    current_canonical_number = int(new_number)
    return current_canonical_number


def increment_current_canonical_number() -> int:
    global current_canonical_number
    current_canonical_number += 1
    if current_canonical_number > 9999:
        current_canonical_number = 1
    while CanonicalNumber.objects.filter(canonical_number=current_canonical_number, is_deleted=False).exists():
        current_canonical_number += 1
    return current_canonical_number


class CanonicalNumber(BaseModel, BaseTimestampModel):
    """
    Canonical Number
    - canonical_number
    - created (from BaseTimestampModel)
    - id (from Basemodel)
    - is_deleted
    - is_retired
    - modified (from BaseTimestampModel)
    """

    canonical_number = models.IntegerField(null=False, blank=False)
    is_deleted = models.BooleanField(default=False)
    is_retired = models.BooleanField(default=False)

    def timestamp(self) -> int:
        return int(round(1000 * datetime.strptime(str(self.created), "%Y-%m-%dT%H:%M:%S.%f%z").timestamp()))
