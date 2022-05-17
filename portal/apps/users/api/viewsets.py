from django.contrib.auth.models import Group
from portal.apps.users.models import AerpawUser, AerpawRolesEnum
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework import permissions
from portal.apps.users.api.serializers import UserSerializer, GroupSerializer
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.status import HTTP_204_NO_CONTENT


class UserViewSet(GenericViewSet, RetrieveModelMixin, ListModelMixin, UpdateModelMixin):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = AerpawUser.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        """
        GET: list users as paginated results
        - display_name
        - email
        - user_id
        - username
        """
        page = self.paginate_queryset(self.queryset)
        if page:
            serializer = UserSerializer(page, many=True)
        else:
            serializer = UserSerializer(self.queryset, many=True)
        response_data = []
        for u in serializer.data:
            du = dict(u)
            response_data.append(
                {
                    'display_name': du.get('display_name'),
                    'email': du.get('oidc_email'),
                    'user_id': du.get('id'),
                    'username': du.get('username')
                }
            )
        if page:
            return self.get_paginated_response(response_data)
        else:
            return Response(response_data)

    def create(self, request):
        """
        POST: user cannot be created via the API
        """
        raise PermissionDenied(detail="user creation is not supported via API")

    def retrieve(self, request, *args, **kwargs):
        """
        GET: retrieve single result
        - pk: sent as kwarg
        """
        user = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        serializer = UserSerializer(user)
        du = dict(serializer.data)
        all_roles = [v for (k, v) in AerpawRolesEnum.choices()]
        all_groups = Group.objects.filter(pk__in=du.get('groups')).values_list('name', flat=True)
        aerpaw_roles = list(filter(lambda x: x in all_groups, all_roles))
        django_groups = list(filter(lambda x: x not in all_groups, aerpaw_roles))
        response_data = {
            'aerpaw_roles': aerpaw_roles,
            'display_name': du.get('display_name'),
            'email': du.get('oidc_email'),
            'groups': django_groups,
            'is_active': du.get('is_active'),
            'oidc_sub': du.get('oidc_sub'),
            'profile': {},
            'user_id': du.get('id'),
            'username': du.get('username')
        }
        return Response(response_data)

    def update(self, request, *args, **kwargs):
        """
        PUT: display_name - only attribute which can be updated
        - pk: sent as kwarg
        - display_name: sent as request data
        """
        user = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        if request.user.id != user.id:
            raise PermissionDenied(detail="user_id does not match requestor id")
        if request.data['display_name']:
            user.display_name = request.data['display_name']
            user.save()

        return Response(status=HTTP_204_NO_CONTENT)

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH: display_name - only attribute which can be updated
        - pk: sent as kwarg
        - display_name: sent as request data
        """
        user = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        if request.user.id != user.id:
            raise PermissionDenied(detail="user_id does not match requestor id")
        if request.data['display_name']:
            user.display_name = request.data['display_name']
            user.save()

        return Response(status=HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """
        DELETE: user cannot be deleted via the API
        """
        raise PermissionDenied(detail="user deletion is not supported via API")


class GroupViewSet(GenericViewSet, ListModelMixin, CreateModelMixin):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        """
        GET: list groups as paginated results
        - group_id (site_admin only)
        - name
        - permissions (site_admin only)
        """
        user = get_object_or_404(AerpawUser.objects.all(), pk=request.user.id)
        page = self.paginate_queryset(self.queryset)
        if page:
            serializer = GroupSerializer(page, many=True)
        else:
            serializer = GroupSerializer(self.queryset, many=True)
        response_data = []
        if user.is_site_admin():
            for g in serializer.data:
                dg = dict(g)
                response_data.append(
                    {
                        'group_id': dg.get('id'),
                        'name': dg.get('name'),
                        'permissions': dg.get('permissions')
                    }
                )
        else:
            for g in serializer.data:
                dg = dict(g)
                response_data.append(
                    {
                        'name': dg.get('name')
                    }
                )
        if page:
            return self.get_paginated_response(response_data)
        else:
            return Response(response_data)

    def create(self, request, *args, **kwargs):
        user = get_object_or_404(AerpawUser.objects.all(), pk=request.user.id)
        if user.is_site_admin():
            response = request.POST
            print(response)
            print(request.data)
        else:
            raise PermissionDenied()
        return Response({"status": 501, "message": "Not Implemented", "details": "create Not Implemented"})

    def retrieve(self, request, pk=None):
        group = get_object_or_404(self.queryset, pk=pk)
        serializer = GroupSerializer(group)
        return Response(serializer.data)

    def update(self, request, pk=None):
        return Response({"status": 501, "message": "Not Implemented", "details": "update Not Implemented"})

    def partial_update(self, request, pk=None):
        return Response({"status": 501, "message": "Not Implemented", "details": "partial_update Not Implemented"})

    def destroy(self, request, pk=None):
        """
        DELETE: group cannot be deleted via the API
        """
        raise PermissionDenied(detail="group deletion is not supported via API")
