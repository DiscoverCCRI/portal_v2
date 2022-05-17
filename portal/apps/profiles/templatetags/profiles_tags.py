
import os
import jwt
from datetime import datetime, timezone

from django import template

register = template.Library()


@register.filter
def token_expiry(token_jwt):
    token_json = jwt.decode(
        jwt=token_jwt,
        key=os.getenv('DJANGO_SECRET_KEY'),
        algorithms=["HS256"],
        options={"verify_aud": False, "verify_signature": False}
    )
    ts = int(token_json.get('exp'))
    utc_date = datetime.fromtimestamp(ts, tz=timezone.utc)

    return utc_date
