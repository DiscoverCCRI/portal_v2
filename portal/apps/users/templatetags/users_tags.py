from django import template

from portal.apps.users.models import AerpawUser

register = template.Library()


@register.filter
def id_to_username(user_id):
    try:
        user = AerpawUser.objects.get(pk=int(user_id))
        return user.username
    except Exception as exc:
        print(exc)
        return 'not found'
