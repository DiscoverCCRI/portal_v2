from enum import Enum

from django.contrib.auth.models import AbstractUser
from django.db import models

from portal.apps.mixins.models import AuditModelMixin, BaseModel
from portal.apps.profiles.models import AerpawUserProfile


class AerpawRolesEnum(Enum):
    EXPERIMENTER = 'experimenter'
    PI = 'pi'
    OPERATOR = 'operator'
    SITE_ADMIN = 'site_admin'

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


class AerpawUser(BaseModel, AuditModelMixin, AbstractUser):
    """
    Extend User model (default fields below)
    reference: https://docs.djangoproject.com/en/4.0/ref/contrib/auth/
    - created (from AuditModelMixin)
    - created_by (from AuditModelMixin)
    - date_joined (from AbstractUser)
    - display_name
    - email (from AbstractUser)
    - first_name (from AbstractUser)
    - groups (from AbstractUser)
    - id (from Basemodel)
    - is_active (from AbstractUser)
    - is_staff (from AbstractUser)
    - is_superuser (from AbstractUser)
    - last_login (from AbstractUser)
    - last_name (from AbstractUser)
    - modified (from AuditModelMixin)
    - modified_by (from AuditModelMixin)
    - openid_sub
    - password (from AbstractUser)
    - profile
    - user_permissions (from AbstractUser)
    - username (from AbstractUser)
    - uuid
    """

    display_name = models.CharField(max_length=255)
    openid_sub = models.CharField(max_length=255)
    profile = models.ForeignKey(
        AerpawUserProfile,
        related_name='+',
        on_delete=models.CASCADE,
        null=True
    )
    public_key = models.TextField(null=True)
    note_public_key = models.TextField(null=True)
    uuid = models.CharField(max_length=255, primary_key=False, editable=False)

    class Meta:
        ordering = ['display_name']

    def __str__(self):
        return self.username

    def is_experimenter(self):
        return self.groups.filter(name=AerpawRolesEnum.EXPERIMENTER.value).exists()

    def is_pi(self):
        return self.groups.filter(name=AerpawRolesEnum.PI.value).exists()

    def is_operator(self):
        return self.groups.filter(name=AerpawRolesEnum.OPERATOR.value).exists()

    def is_site_admin(self):
        return self.groups.filter(name=AerpawRolesEnum.SITE_ADMIN.value).exists()
