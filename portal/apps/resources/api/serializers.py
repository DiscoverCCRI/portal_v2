from rest_framework import serializers

from portal.apps.resources.models import AerpawResource


class ResourceSerializerList(serializers.ModelSerializer):
    resource_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = AerpawResource
        fields = ['description', 'is_active', 'location', 'name', 'resource_class', 'resource_id',
                  'resource_mode', 'resource_type']


class ResourceSerializerDetail(serializers.ModelSerializer):
    created_date = serializers.DateTimeField(source='created')
    last_modified_by = serializers.CharField(source='modified_by')
    modified_date = serializers.DateTimeField(source='modified')
    resource_creator = serializers.CharField(source='created_by')
    resource_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = AerpawResource
        fields = ['created_date', 'description', 'hostname', 'ip_address', 'is_active', 'is_deleted',
                  'last_modified_by', 'location', 'modified_date', 'name', 'ops_notes', 'resource_class',
                  'resource_creator', 'resource_id', 'resource_mode', 'resource_type']
