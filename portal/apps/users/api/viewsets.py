from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed, PermissionDenied, ValidationError
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from portal.apps.users.api.serializers import UserSerializerDetail, UserSerializerList, UserSerializerTokens
from portal.apps.users.models import AerpawUser

# constants
USER_MIN_DISPLAY_NAME_LEN = 5


class UserViewSet(GenericViewSet, RetrieveModelMixin, ListModelMixin, UpdateModelMixin):
    """
    AERPAW Users
    - get list
    - get one
    - update
    - get user credentials
    - get user tokens
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = AerpawUser.objects.all().order_by('display_name')
    serializer_class = UserSerializerDetail

    def get_queryset(self):
        """
        Optional parameter: search
        """
        search = self.request.query_params.get('search', None)
        if search:
            queryset = AerpawUser.objects.filter(
                Q(display_name__icontains=search) |
                Q(email__icontains=search)
            ).order_by('display_name')
        else:
            queryset = AerpawUser.objects.all().order_by('display_name')
        return queryset

    def list(self, request, *args, **kwargs):
        """
        GET: list users as paginated results (search)
        - display_name:          - string
        - email                  - string
        - user_id                - int
        - username               - string

        Permission:
        - active users
        """
        if request.user.is_active:
            page = self.paginate_queryset(self.get_queryset())
            if page:
                serializer = UserSerializerList(page, many=True)
            else:
                serializer = UserSerializerList(self.get_queryset(), many=True)
            response_data = []
            for u in serializer.data:
                du = dict(u)
                response_data.append(
                    {
                        'display_name': du.get('display_name'),
                        'email': du.get('email'),
                        'user_id': du.get('user_id'),
                        'username': du.get('username')
                    }
                )
            if page:
                return self.get_paginated_response(response_data)
            else:
                return Response(response_data)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to GET /users list")

    def create(self, request):
        """
        POST: user cannot be created via the API
        """
        raise MethodNotAllowed(method="POST: /users")

    def retrieve(self, request, *args, **kwargs):
        """
        GET: retrieve single result
        - aerpaw_roles           - array of roles
        - display_name           - string
        - email                  - string
        - is_active              - boolean
        - openid_sub             - string
        - user_id                - int
        - username               - string

        Permission:
        - user is_self
        - user is_operator
        """
        user = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        if request.user.id == user.id or request.user.is_operator():
            serializer = UserSerializerDetail(user)
            du = dict(serializer.data)
            response_data = {
                'aerpaw_roles': [r.get('role') for r in du.get('aerpaw_roles')],
                'display_name': du.get('display_name'),
                'email': du.get('email'),
                'is_active': du.get('is_active'),
                'openid_sub': du.get('openid_sub'),
                'user_id': du.get('user_id'),
                'username': du.get('username')
            }
            return Response(response_data)
        elif request.user.is_active:
            serializer = UserSerializerDetail(user)
            du = dict(serializer.data)
            response_data = {
                'display_name': du.get('display_name'),
                'email': du.get('email'),
                'user_id': du.get('user_id'),
                'username': du.get('username')
            }
            return Response(response_data)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to GET /users/{0} details".format(kwargs.get('pk')))

    def update(self, request, *args, **kwargs):
        """
        PUT: update user as self
        - display_name           - string

        Permission:
        - user is_self
        """
        user = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        if request.user.id == user.id:
            if request.data.get('display_name', None):
                if len(request.data.get('display_name')) < USER_MIN_DISPLAY_NAME_LEN:
                    raise ValidationError(
                        detail="display_name: must be at least {0} chars long".format(USER_MIN_DISPLAY_NAME_LEN))
                user.display_name = request.data.get('display_name')
                user.save()
            return self.retrieve(request, pk=user.id)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to PUT/PATCH /users/{0} details".format(kwargs.get('pk')))

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH: update user as self
        - display_name           - string

        Permission:
        - user is_self
        """
        return self.update(request, *args, **kwargs)

    def destroy(self, request, pk=None):
        """
        DELETE: user cannot be deleted via the API
        """
        raise MethodNotAllowed(method="DELETE: /users/{user_id}")

    @action(detail=True, methods=['get'])
    def credentials(self, request, *args, **kwargs):
        """
        GET: credentials
        - name                   - string
        - public_key_credential  - string
        - public_key_id          - int

        Permission:
        - user is_self
        """
        user = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        if request.user.id == user.id:
            # TODO: credential serializer and response
            response_data = {}
            return Response(response_data)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to GET /users/{0}/credentials".format(kwargs.get('pk')))

    @action(detail=True, methods=['get'])
    def tokens(self, request, *args, **kwargs):
        """
        GET: tokens
        - access_token           - string
        - refresh_token          - string

        Permission:
        - user is_self
        """
        user = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        if request.user.id == user.id:
            serializer = UserSerializerTokens(user)
            du = dict(serializer.data)
            response_data = {
                'access_token': du.get('access_token'),
                'refresh_token': du.get('refresh_token')
            }
            return Response(response_data)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to GET /users/{0}/tokens".format(kwargs.get('pk')))
