# Mixins

Abstract base models from which to extend

Most models will inherit `BaseModel` and `AuditModelMixin`

### BaseModel

Simply define `id` in a standard way across all models

```python
class BaseModel(models.Model):
    id = models.AutoField(
        primary_key=True,
        unique=True,
        editable=False
    )
    
    class Meta:
        abstract = True
```

### BaseTimeStampModel

Timestamps for object creation and modification

```python
class BaseTimestampModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
        
    class Meta:
        abstract = True
```

### BaseTrackingModel

Emails associated to object creation and modification

```python
class BaseTrackingModel(models.Model):
    created_by = models.EmailField()
    modified_by = models.EmailField()
        
    class Meta:
        abstract = True
```

### AuditModelMixin

Combination of TimeStamp and Tracking

```python
class AuditModelMixin(BaseTimestampModel, BaseTrackingModel):
    """
    Mixin that provides created_by, created, modified_by, modified fields
    Includes
    - BaseTimestampModel
    - BaseTrackingModel
    """
    
    class Meta:
        abstract = True
```
