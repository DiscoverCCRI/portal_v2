from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from portal.apps.mixins.models import AuditModelMixin, BaseModel
from portal.apps.operations.models import CanonicalNumber
from portal.apps.users.models import AerpawUser
from portal.apps.projects.models import AerpawProject
from portal.apps.resources.models import AerpawResource


class AerpawExperiment(BaseModel, AuditModelMixin, models.Model):
    """
    Experiment
    - canonical_number
    - created (from AuditModelMixin)
    - created_by (from AuditModelMixin)
    - description
    - experiment_members
    - experiment_state
    - id (from Basemodel)
    - is_canonical
    - is_retired
    - modified (from AuditModelMixin)
    - modified_by (from AuditModelMixin)
    - name
    - project
    - resources
    - uuid
    """
    class ExperimentState(models.TextChoices):
        ACTIVE_DEVELOPMENT = 'active_development', _('Active Development')
        ACTIVE_EMULATION = 'active_emulation', _('Active Emulation')
        ACTIVE_SANDBOX = 'active_sandbox', _('Active Sandbox')
        ACTIVE_TESTBED = 'active_testbed', _('Active Testbed')
        SAVED = 'saved', _('Saved')
        WAIT_DEVELOPMENT_DEPLOY = 'wait_development_deploy', _('Wait Development Deploy')
        WAIT_EMULATION_DEPLOY = 'wait_emulation_deploy', _('Wait Emulation Deploy')
        WAIT_SANDBOX_DEPLOY = 'wait_sandbox_deploy', _('Wait Sandbox Deploy')
        WAIT_TESTBED_DEPLOY = 'wait_testbed_deploy', _('Wait Testbed Deploy')

    canonical_number = models.ForeignKey(
        CanonicalNumber,
        related_name='canonical_experiment_number',
        on_delete=models.PROTECT
    )
    description = models.TextField(blank=False, null=False)
    experiment_creator = models.ForeignKey(
        AerpawUser,
        related_name='experiment_creator',
        on_delete=models.PROTECT
    )
    experiment_members = models.ManyToManyField(
        AerpawUser,
        related_name='experiment_members',
        through='UserExperiment',
        through_fields=('experiment', 'user')
    )
    experiment_state = models.CharField(
        max_length=255,
        choices=ExperimentState.choices,
        default=ExperimentState.ACTIVE_DEVELOPMENT
    )
    is_canonical = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_retired = models.BooleanField(default=False)
    name = models.CharField(max_length=255, blank=False, null=False)
    project = models.ForeignKey(
        AerpawProject,
        related_name='experiment_project',
        on_delete=models.PROTECT
    )
    resources = models.ManyToManyField(
        AerpawResource,
        related_name='experiment_resources'
    )
    uuid = models.CharField(max_length=255, primary_key=False, editable=False)

    class Meta:
        verbose_name = 'AERPAW Experiment'

    def __str__(self):
        return self.name

    def state(self):
        return self.experiment_state


class UserExperiment(BaseModel, models.Model):
    """
    User-Experiment relationship
    - experiment_id
    - granted_by
    - granted_date
    - id (from Basemodel)
    - user_id
    """
    experiment = models.ForeignKey(AerpawExperiment, on_delete=models.CASCADE)
    granted_by = models.ForeignKey(AerpawUser, related_name='experiment_granted_by', on_delete=models.CASCADE)
    granted_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(AerpawUser, related_name='experiment_user', on_delete=models.CASCADE)
