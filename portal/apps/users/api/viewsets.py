from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed, PermissionDenied
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.viewsets import GenericViewSet

from portal.apps.users.api.serializers import UserSerializerDetail, UserSerializerList, UserSerializerTokens
from portal.apps.users.models import AerpawUser


class UserViewSet(GenericViewSet, RetrieveModelMixin, ListModelMixin, UpdateModelMixin):
    """
    API endpoint that allows users to be viewed or edited.
    """
    serializer_class = UserSerializerDetail
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        try:
            search = self.request.query_params.get('search', None)
            if search:
                queryset = AerpawUser.objects.filter(
                    Q(display_name__icontains=search) |
                    Q(email__icontains=search)
                ).order_by('display_name')
            else:
                queryset = AerpawUser.objects.all().order_by('display_name')
        except Exception as exc:
            print(exc)
            queryset = AerpawUser.objects.all().order_by('display_name')
        return queryset

    def list(self, request, *args, **kwargs):
        """
        GET: list users as paginated results
        - display_name
        - email
        - user_id
        - username
        """
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

    def create(self, request):
        """
        POST: user cannot be created via the API
        """
        raise MethodNotAllowed(method="POST: /users")

    def retrieve(self, request, *args, **kwargs):
        """
        GET: retrieve single result
        - pk: sent as kwarg
        """
        user = get_object_or_404(self.get_queryset(), pk=kwargs.get('pk'))
        serializer = UserSerializerDetail(user)
        du = dict(serializer.data)
        response_data = {
            'aerpaw_roles': du.get('aerpaw_roles'),
            'display_name': du.get('display_name'),
            'email': du.get('email'),
            'is_active': du.get('is_active'),
            'openid_sub': du.get('openid_sub'),
            'user_id': du.get('user_id'),
            'username': du.get('username')
        }
        return Response(response_data)

    def update(self, request, *args, **kwargs):
        """
        PUT: display_name - only attribute which can be updated
        - pk: sent as kwarg
        - display_name: sent as request data
        """
        user = get_object_or_404(self.get_queryset(), pk=kwargs.get('pk'))
        if request.user.id != user.id:
            raise PermissionDenied(detail="user_id does not match requestor id")
        if request.data.get('display_name', None):
            user.display_name = request.data.get('display_name')
            user.save()
            return Response(status=HTTP_204_NO_CONTENT)
        else:
            return Response(status=HTTP_204_NO_CONTENT)

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH: display_name - only attribute which can be updated
        - pk: sent as kwarg
        - display_name: sent as request data
        """
        user = get_object_or_404(self.get_queryset(), pk=kwargs.get('pk'))
        if request.user.id != user.id:
            raise PermissionDenied(detail="user_id does not match requestor id")
        if request.data.get('display_name', None):
            user.display_name = request.data.get('display_name')
            user.save()
            return Response(status=HTTP_204_NO_CONTENT)
        else:
            return Response(status=HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """
        DELETE: user cannot be deleted via the API
        """
        raise MethodNotAllowed(method="DELETE: /users/{user_id}")

    @action(detail=True, methods=['get'])
    def tokens(self, request, *args, **kwargs):
        """
        GET: retrieve access_token and refresh_token
        - pk: sent as kwarg
        """
        user = get_object_or_404(self.get_queryset(), pk=kwargs.get('pk'))
        if request.user.id != user.id:
            raise PermissionDenied(detail="user_id does not match requestor id")
        serializer = UserSerializerTokens(user)
        du = dict(serializer.data)
        response_data = {
            'access_token': du.get('access_token'),
            'refresh_token': du.get('refresh_token')
        }
        return Response(response_data)

    @action(detail=True, methods=['get'])
    def credentials(self, request, *args, **kwargs):
        """
        GET: list user credentials
        - pk: sent as kwarg
        """
        user = get_object_or_404(self.get_queryset(), pk=kwargs.get('pk'))
        if request.user.id != user.id:
            raise PermissionDenied(detail="user_id does not match requestor id")
        # TODO: credential serializer and response
        response_data = []
        return Response(response_data)
