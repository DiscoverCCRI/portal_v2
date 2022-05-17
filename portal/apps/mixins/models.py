from django.db import models


class BaseModel(models.Model):
    id = models.AutoField(
        primary_key=True,
        unique=True,
        editable=False
    )

    class Meta:
        abstract = True


class BaseTimestampModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseTrackingModel(models.Model):
    created_by = models.EmailField()
    modified_by = models.EmailField()

    class Meta:
        abstract = True


class AuditModelMixin(BaseTimestampModel, BaseTrackingModel):
    """
    Mixin that provides created_by, created, modified_by, modified fields
    Includes
        - BaseTimestampModel
        - BaseTrackingModel
    """

    class Meta:
        abstract = True
