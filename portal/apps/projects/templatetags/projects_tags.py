from django import template

from portal.apps.projects.models import AerpawProject

register = template.Library()


@register.filter
def id_to_project_name(project_id):
    try:
        project = AerpawProject.objects.get(pk=int(project_id))
        return project.name
    except Exception as exc:
        print(exc)
        return 'not found'
