from rest_framework import serializers

from portal.apps.projects.models import AerpawProject, UserProject


class UserProjectSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id')
    role = serializers.CharField(source='project_role')

    class Meta:
        model = UserProject
        fields = ['user_id', 'role']


class ProjectSerializerList(serializers.ModelSerializer):
    created_date = serializers.DateTimeField(source='created')
    project_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = AerpawProject
        fields = ['created_date', 'description', 'is_public', 'name', 'project_creator', 'project_id']


class ProjectSerializerDetail(serializers.ModelSerializer):
    created_date = serializers.DateTimeField(source='created')
    last_modififed_by = serializers.CharField(source='modified_by')
    modified_date = serializers.DateTimeField(source='modified')
    project_id = serializers.IntegerField(source='id', read_only=True)
    project_personnel = UserProjectSerializer(source='userproject_set', many=True)

    class Meta:
        model = AerpawProject
        fields = ['created_date', 'description', 'is_public', 'last_modififed_by', 'modified_date', 'name',
                  'project_creator', 'project_id', 'project_personnel']
