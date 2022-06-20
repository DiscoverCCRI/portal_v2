from django.contrib.auth.models import Group
from rest_framework import serializers

from portal.apps.users.models import AerpawUser


class GroupSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='name')

    class Meta:
        model = Group
        fields = ['role', ]


class UserSerializerList(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = AerpawUser
        fields = ['display_name', 'email', 'user_id', 'username', ]


class UserSerializerDetail(serializers.ModelSerializer):
    aerpaw_roles = GroupSerializer(source='groups', many=True)
    user_id = serializers.IntegerField(source='id')

    class Meta:
        model = AerpawUser
        fields = ['aerpaw_roles', 'display_name', 'email', 'is_active', 'openid_sub', 'user_id', 'username', ]


class UserSerializerTokens(serializers.ModelSerializer):
    access_token = serializers.CharField(source='profile.access_token')
    refresh_token = serializers.CharField(source='profile.refresh_token')

    class Meta:
        model = AerpawUser
        fields = ['access_token', 'refresh_token', ]
