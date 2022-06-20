from django.contrib.auth.models import AbstractUser
from django.db import models

from portal.apps.mixins.models import AuditModelMixin, BaseModel
from portal.apps.profiles.models import AerpawUserProfile
from portal.apps.users.models import AerpawUser


class AerpawProject(BaseModel, AuditModelMixin, models.Model):
    """
    Projects
    - created (from AuditModelMixin)
    - created_by (from AuditModelMixin)
    - description
    - id (from Basemodel)
    - is_public
    - modified (from AuditModelMixin)
    - modified_by (from AuditModelMixin)
    - name
    - project_creator (fk)
    - project_members (m2m)
    - project_owners (m2m)
    - uuid
    """
    description = models.TextField()
    is_public = models.BooleanField(default=False)
    name = models.CharField(max_length=255, blank=False, null=False)
    personnel = models.ManyToManyField(
        AerpawUser,
        related_name='+',
        through='ProjectPersonnel',
        through_fields=('project', 'user')
    )
    project_creator = models.ForeignKey(
        AerpawUser, related_name='project_creator',
        on_delete=models.PROTECT
    )
    uuid = models.CharField(max_length=255, primary_key=False, editable=False)

    class Meta:
        verbose_name = 'AERPAW Project'

    def __str__(self):
        return self.name

    def is_creator(self, user: AerpawUser) -> bool:
        return user == self.project_creator

    def is_member(self, user: AerpawUser) -> bool:
        return ProjectPersonnel.objects.filter(user=user, project=self, is_project_member=True).exists()

    def is_owner(self, user: AerpawUser) -> bool:
        return ProjectPersonnel.objects.filter(user=user, project=self, is_project_owner=True).exists()


class ProjectPersonnel(BaseModel, models.Model):
    """
    Project Personnel
    """
    granted_by = models.ForeignKey(AerpawUser, related_name='project_granted_by', on_delete=models.CASCADE)
    granted_date = models.DateTimeField(auto_now_add=True)
    is_project_member = models.BooleanField(default=False)
    is_project_owner = models.BooleanField(default=False)
    project = models.ForeignKey(AerpawProject, on_delete=models.CASCADE)
    user = models.ForeignKey(AerpawUser, related_name='project_user', on_delete=models.CASCADE)
