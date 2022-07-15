import json
import os
from datetime import datetime, timezone

from django.db import models

from portal.apps.mixins.models import BaseModel, BaseTimestampModel
from portal.server.settings import BASE_DIR

# constants
MAX_CANONICAL_NUMBER = 9999
CANONICAL_NUMBER_JSON = 'apps/operations/current-canonical-number.json'

# global for Canonical Number
current_canonical_number = 0


def _read_current_canonical_number() -> int:
    print('### read_current_canonical_number()')
    try:
        file_path = os.path.join(BASE_DIR, CANONICAL_NUMBER_JSON)
        with open(file_path, "r") as file:
            file_dict = json.load(file)
        if file_dict.get('current_canonical_number', None):
            return int(file_dict.get('current_canonical_number'))
    except Exception as exc:
        print(exc)

    return 0


def _write_current_canonical_number(canonical_number: int):
    print('### write_current_canonical_number()')
    file_path = os.path.join(BASE_DIR, CANONICAL_NUMBER_JSON)
    file_dict = {
        "current_canonical_number": canonical_number,
        "timestamp": int(round(datetime.now(timezone.utc).timestamp()))
    }
    file_json = json.dumps(file_dict, indent=4)
    with open(file_path, "w") as file:
        file.write(file_json)


def get_current_canonical_number() -> int:
    global current_canonical_number
    current_canonical_number = _read_current_canonical_number()
    if CanonicalNumber.objects.filter(canonical_number=current_canonical_number, is_deleted=False).exists() or \
            int(current_canonical_number) < 1 or int(current_canonical_number) > 9999:
        return increment_current_canonical_number()
    _write_current_canonical_number(current_canonical_number)
    return current_canonical_number


def set_current_canonical_number(new_number: int = None) -> int:
    global current_canonical_number
    current_canonical_number = int(new_number)
    _write_current_canonical_number(current_canonical_number)
    return current_canonical_number


def increment_current_canonical_number() -> int:
    global current_canonical_number
    current_canonical_number += 1
    if current_canonical_number < 1 or current_canonical_number > 9999:
        current_canonical_number = 1
    while CanonicalNumber.objects.filter(canonical_number=current_canonical_number, is_deleted=False).exists():
        current_canonical_number += 1
    _write_current_canonical_number(current_canonical_number)
    return current_canonical_number


class CanonicalNumber(BaseModel, BaseTimestampModel, models.Model):
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
        return int(round(datetime.strptime(str(self.created), "%Y-%m-%d %H:%M:%S.%f%z").timestamp()))
