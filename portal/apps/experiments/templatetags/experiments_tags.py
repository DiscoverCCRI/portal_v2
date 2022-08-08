from django import template

from portal.apps.experiments.models import AerpawExperiment

register = template.Library()


@register.filter
def id_to_experiment_name(experiment_id):
    try:
        experiment = AerpawExperiment.objects.get(pk=int(experiment_id))
        return experiment.name
    except Exception as exc:
        print(exc)
        return 'not found'
