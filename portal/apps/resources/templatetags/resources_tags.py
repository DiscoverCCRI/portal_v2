from django import template

from portal.apps.resources.models import AerpawResource

register = template.Library()


@register.filter
def id_to_resource_name(resource_id):
    try:
        resource = AerpawResource.objects.get(pk=int(resource_id))
        return resource.name
    except Exception as exc:
        print(exc)
        return 'not found'
