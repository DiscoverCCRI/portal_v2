from rest_framework import serializers

from portal.apps.projects.models import AerpawProject, UserProject


class UserProjectSerializer(serializers.ModelSerializer):
    project_id = serializers.IntegerField(source='project.id')
    user_id = serializers.IntegerField(source='user.id')

    class Meta:
        model = UserProject
        fields = ['granted_by', 'granted_date', 'id', 'project_id', 'project_role', 'user_id']


class ProjectSerializerList(serializers.ModelSerializer):
    created_date = serializers.DateTimeField(source='created')
    project_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = AerpawProject
        fields = ['created_date', 'description', 'is_public', 'name', 'project_creator', 'project_id']


class ProjectSerializerDetail(serializers.ModelSerializer):
    created_date = serializers.DateTimeField(source='created')
    last_modified_by = serializers.CharField(source='modified_by')
    modified_date = serializers.DateTimeField(source='modified')
    project_id = serializers.IntegerField(source='id', read_only=True)
    project_personnel = UserProjectSerializer(source='userproject_set', many=True)

    class Meta:
        model = AerpawProject
        fields = ['created_date', 'description', 'is_deleted', 'is_public', 'last_modified_by', 'modified_date',
                  'name', 'project_creator', 'project_id', 'project_personnel']
