from uuid import uuid4

from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from portal.apps.projects.api.serializers import ProjectPersonnelSerializer, ProjectSerializer
from portal.apps.projects.models import AerpawProject, ProjectPersonnel
from portal.apps.users.models import AerpawUser


class ProjectViewSet(GenericViewSet, RetrieveModelMixin, ListModelMixin, UpdateModelMixin):
    """
    API endpoint that allows projects to be viewed or edited.
    """
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        search = self.request.query_params.get('search', None)
        if search:
            queryset = AerpawProject.objects.filter(
                name__icontains=search
            ).order_by('name')
        else:
            queryset = AerpawProject.objects.all().order_by('name')
        return queryset

    def list(self, request, *args, **kwargs):
        """
        GET: list projects as paginated results
        - created_date           - UTC timestamp
        - description            - string
        - is_public              - bool
        - last_modified_by (fk)  - user_ID
        - modified_date          - UTC timestamp
        - name                   - string
        - project_creator (fk)   - user_ID
        - project_ID (pk)        - integer
        """
        page = self.paginate_queryset(self.get_queryset())
        if page:
            serializer = ProjectSerializer(page, many=True)
        else:
            serializer = ProjectSerializer(self.get_queryset(), many=True)
        response_data = []
        for u in serializer.data:
            du = dict(u)
            try:
                project_creator = AerpawUser.objects.get(username=du.get('created_by')).id
            except AerpawUser.DoesNotExist:
                project_creator = None
            try:
                last_modified_by = AerpawUser.objects.get(username=du.get('modified_by')).id
            except AerpawUser.DoesNotExist:
                last_modified_by = None
            response_data.append(
                {
                    'created_date': du.get('created'),
                    'description': du.get('description'),
                    'is_public': du.get('is_public'),
                    'last_modified_by': last_modified_by,
                    'modified_date': du.get('modified'),
                    'name': du.get('name'),
                    'project_creator': project_creator,
                    'project_id': du.get('id')
                }
            )
        if page:
            return self.get_paginated_response(response_data)
        else:
            return Response(response_data)

    def create(self, request):
        """
        POST: project cannot be created via the API
        """
        user = get_object_or_404(AerpawUser.objects.all(), pk=request.user.id)
        if user.is_pi():
            # check name
            name = request.data.get('name', None)
            if not name:
                raise ValidationError(detail="name: Project must define a name (string)")
            # check description
            description = request.data.get('description', None)
            if not description:
                raise ValidationError(detail="description: Project must define a description (string)")
            # check is_pubic
            is_public = str(request.data.get('is_public')).casefold() == 'true'
            # create project
            project = AerpawProject()
            project.created_by = user.username
            project.project_creator = user
            project.description = description
            project.is_public = is_public
            project.modified_by = user.username
            project.name = name
            project.uuid = uuid4()
            project.save()
            # set creator as project_owner
            personnel = ProjectPersonnel()
            personnel.granted_by = user
            personnel.is_project_owner = True
            personnel.project = project
            personnel.user = user
            personnel.save()
        else:
            raise PermissionDenied(
                detail="User: '{0}' does not have permission to create a project".format(user.username))
        kwargs = {'pk': project.id}
        # return project object
        return self.retrieve(request, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        GET: retrieve single result
        - pk: sent as kwarg
        """
        project = get_object_or_404(self.get_queryset(), pk=kwargs.get('pk'))
        serializer = ProjectSerializer(project)
        du = dict(serializer.data)
        try:
            project_creator = AerpawUser.objects.get(username=du.get('created_by')).id
        except AerpawUser.DoesNotExist:
            project_creator = None
        try:
            last_modified_by = AerpawUser.objects.get(username=du.get('modified_by')).id
        except AerpawUser.DoesNotExist:
            last_modified_by = None
        project_members = []
        project_owners = []
        for user_id in du.get('personnel'):
            if ProjectPersonnel.objects.filter(project=project, user__id=user_id, is_project_member=True).exists():
                project_members.append(user_id)
            if ProjectPersonnel.objects.filter(project=project, user__id=user_id, is_project_owner=True).exists():
                project_owners.append(user_id)
        response_data = {
            'created_date': du.get('created'),
            'description': du.get('description'),
            'is_public': du.get('is_public'),
            'last_modified_by': last_modified_by,
            'modified_date': du.get('modified'),
            'name': du.get('name'),
            'project_creator': project_creator,
            'project_id': du.get('id'),
            'project_members': project_members,
            'project_owners': project_owners
        }
        return Response(response_data)

    def update(self, request, *args, **kwargs):
        """
        PUT: description, name - only attributes which can be partially updated
        - pk: sent as kwarg
        - description, name: sent as request data
        """
        project = get_object_or_404(AerpawProject.objects.all(), pk=kwargs.get('pk'))
        # verify that user is a project_owner (or the project creator)
        user = get_object_or_404(AerpawUser.objects.all(), pk=request.user.id)
        if not project.is_creator(user) and not project.is_owner(user):
            raise PermissionDenied(detail="User '{0}' is not a project owner".format(user.display_name))
        # check for description
        if request.data.get('description', None):
            project.description = request.data.get('description')
            project.modified_by = user.email
            project.save()
        # check for name
        if request.data.get('name', None):
            project.modified_by = user.email
            project.name = request.data.get('name')
            project.save()

        kwargs = {'pk': project.id}
        # return project object
        return self.retrieve(request, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH: description, name - only attributes which can be partially updated
        - pk: sent as kwarg
        - description, name: sent as request data
        """
        project = get_object_or_404(AerpawProject.objects.all(), pk=kwargs.get('pk'))
        # verify that user is a project_owner (or the project creator)
        user = get_object_or_404(AerpawUser.objects.all(), pk=request.user.id)
        if not project.is_creator(user) and not project.is_owner(user):
            raise PermissionDenied(detail="User '{0}' is not a project owner".format(user.display_name))
        # check for description
        if request.data.get('description', None):
            project.description = request.data.get('description')
            project.modified_by = user.email
            project.save()
        # check for name
        if request.data.get('name', None):
            project.modified_by = user.email
            project.name = request.data.get('name')
            project.save()

        kwargs = {'pk': project.id}
        # return project object
        return self.retrieve(request, **kwargs)

    def destroy(self, request, pk=None):
        """
        DELETE: project cannot be deleted via the API
        """
        raise PermissionDenied(detail="project deletion is not supported via API")

    @action(detail=True, methods=['get', 'put', 'patch'])
    def personnel(self, request, *args, **kwargs):
        """
        GET: retrieve project_members and project_owners
        - pk: sent as kwarg
        """
        project = get_object_or_404(self.get_queryset(), pk=kwargs.get('pk'))
        personnel = ProjectPersonnel.objects.filter(project=project).all()
        serializer = ProjectPersonnelSerializer(personnel, many=True)
        print(request.method)
        if request.method.casefold() in ['put', 'patch']:
            print(request.data)
        # project_members and project_owners
        project_members = []
        project_owners = []
        for u in serializer.data:
            du = dict(u)
            person = {
                'granted_by': du.get('granted_by'),
                'granted_date': str(du.get('granted_date')),
                'user_id': du.get('user')
            }
            if du.get('is_project_member'):
                project_members.append(person)
            if du.get('is_project_owner'):
                project_owners.append(person)
        response_data = {
            'project_members': project_members,
            'project_owners': project_owners
        }
        return Response(response_data)
