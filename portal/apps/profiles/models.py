from django.contrib.auth.models import AbstractUser
from django.db import models

from portal.apps.mixins.models import AuditModelMixin, BaseModel


class AerpawUserProfile(BaseModel, AuditModelMixin):
    """
    User Profile
    - access_token
    - created (from AuditModelMixin)
    - created_by (from AuditModelMixin)
    - id (from Basemodel)
    - modified (from AuditModelMixin)
    - modified_by (from AuditModelMixin)
    - refresh_token
    - uuid
    """
    # add additional user fields
    access_token = models.TextField(null=True, blank=True)
    refresh_token = models.TextField(null=True, blank=True)
    uuid = models.CharField(max_length=255, primary_key=False, editable=False)

    def __str__(self):
        return self.uuid


class PublicCredentials(BaseModel, AuditModelMixin):
    """
    Public User Credentials
    - created (from AuditModelMixin)
    - created_by (from AuditModelMixin)
    - id (from Basemodel)
    - modified (from AuditModelMixin)
    - modified_by (from AuditModelMixin)
    - uuid
    """
