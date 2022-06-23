from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from portal.apps.mixins.models import AuditModelMixin, BaseModel


class AerpawResource(BaseModel, AuditModelMixin, models.Model):
    """
    Resource
    - created (from AuditModelMixin)
    - created_by (from AuditModelMixin)
    - description
    - hostname
    - id (from Basemodel)
    - ip_address
    - is_active
    - is_deleted
    - location
    - modified (from AuditModelMixin)
    - modified_by (from AuditModelMixin)
    - name
    - ops_notes
    - resource_class
    - resource_mode
    - resource_type
    - uuid
    """

    class ResourceClass(models.TextChoices):
        CANONICAL = 'canonical', _('Canonical')
        NON_CANONICAL = 'non_canonical', _('Non Canonical')

    class ResourceMode(models.TextChoices):
        SANDBOX = 'sandbox', _('Sandbox')
        TESTBED = 'testbed', _('Testbed')

    class ResourceType(models.TextChoices):
        AFRN = 'AFRN', _('AFRN')
        APRN = 'APRN', _('APRN')
        UAV = 'UAV', _('UAV')
        UGV = 'UGV', _('UGV')
        THREE_PBBE = '3PBBE', _('3PBBE')
        OTHER = 'other', _('Other')

    description = models.TextField(blank=False, null=False)
    hostname = models.CharField(max_length=255, blank=True, null=True)
    ip_address = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    location = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=False, null=False)
    ops_notes = models.TextField(blank=True, null=True)
    resource_class = models.CharField(
        max_length=255,
        choices=ResourceClass.choices,
        default=ResourceClass.CANONICAL
    )
    resource_mode = models.CharField(
        max_length=255,
        choices=ResourceMode.choices,
        default=ResourceMode.SANDBOX
    )
    resource_type = models.CharField(
        max_length=255,
        choices=ResourceType.choices,
        default=ResourceType.AFRN
    )
    uuid = models.CharField(max_length=255, primary_key=False, editable=False)

    class Meta:
        verbose_name = 'AERPAW Resource'

    def __str__(self):
        return self.name

    def is_canonical(self):
        return self.resource_class == self.ResourceClass.CANONICAL
