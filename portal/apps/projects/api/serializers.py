from rest_framework import serializers

from portal.apps.projects.models import AerpawProject, ProjectPersonnel


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = AerpawProject
        fields = '__all__'


class ProjectPersonnelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectPersonnel
        fields = '__all__'
