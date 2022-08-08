from datetime import datetime

from django import template

from portal.apps.users.models import AerpawUser

register = template.Library()


@register.filter
def id_to_display_name(user_id):
    try:
        user = AerpawUser.objects.get(pk=int(user_id))
        return user.display_name
    except Exception as exc:
        print(exc)
        return 'not found'


@register.filter
def id_to_username(user_id):
    try:
        user = AerpawUser.objects.get(pk=int(user_id))
        return user.username
    except Exception as exc:
        print(exc)
        return 'not found'


@register.filter
def str_to_datetime(datetime_str):
    try:
        return datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%f%z")
    except Exception as exc:
        print(exc)
        return datetime_str
