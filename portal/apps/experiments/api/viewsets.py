from uuid import uuid4

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed, PermissionDenied, ValidationError
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.viewsets import GenericViewSet

from portal.apps.experiments.api.serializers import ExperimentSerializerList, ExperimentSerializerDetail
from portal.apps.experiments.models import AerpawExperiment, UserExperiment
from portal.apps.users.models import AerpawUser
from portal.apps.projects.models import AerpawProject
from portal.apps.operations.models import CanonicalNumber, get_current_canonical_number, increment_current_canonical_number

# constants
EXPERIMENT_MIN_NAME_LEN = 5
EXPERIMENT_MIN_DESC_LEN = 5


class ExperimentViewSet(GenericViewSet, RetrieveModelMixin, ListModelMixin, UpdateModelMixin):
    """
    AERPAW Experiments
    - paginated list
    - retrieve one
    - create
    - update
    - delete
    - resources
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = AerpawExperiment.objects.all().order_by('name')
    serializer_class = ExperimentSerializerDetail

    def get_queryset(self):
        search = self.request.query_params.get('search', None)
        user = self.request.user
        if search:
            if user.is_operator():
                queryset = AerpawExperiment.objects.filter(is_deleted=False, name__icontains=search).order_by('name')
            else:
                queryset = AerpawExperiment.objects.filter(
                    Q(is_deleted=False, name__icontains=search) &
                    (Q(project__project_personnel__email__in=[user.email]) | Q(project__project_creator=user))
                ).order_by('name')
        else:
            if user.is_operator():
                queryset = AerpawExperiment.objects.filter(is_deleted=False).order_by('name')
            else:
                queryset = AerpawExperiment.objects.filter(
                    Q(is_deleted=False) &
                    (Q(project__project_personnel__email__in=[user.email]) | Q(project__project_creator=user))
                ).order_by('name')
        return queryset

    def list(self, request, *args, **kwargs):
        """
        GET: list experiments as paginated results
        - canonical_number       - int
        - created_date           - string
        - description            - string
        - experiment_creator     - user_ID
        - experiment_id          - int
        - experiment_state       - string
        - is_canonical           - boolean
        - is_retired             - boolean
        - name                   - string

        Permission:
        - user is_experiment_project_personnel
        - user is_experiment_project_creator
        - user is_operator
        """
        if request.user.is_active:
            page = self.paginate_queryset(self.get_queryset())
            if page:
                serializer = ExperimentSerializerList(page, many=True)
            else:
                serializer = ExperimentSerializerList(self.get_queryset(), many=True)
            response_data = []
            for u in serializer.data:
                du = dict(u)
                response_data.append(
                    {
                        'canonical_number': du.get('canonical_number'),
                        'created_date': du.get('created_date'),
                        'description': du.get('description'),
                        'experiment_creator': du.get('experiment_creator'),
                        'experiment_id': du.get('experiment_id'),
                        'is_canonical': du.get('is_canonical'),
                        'is_retired': du.get('is_retired'),
                        'name': du.get('name')
                    }
                )
            if page:
                return self.get_paginated_response(response_data)
            else:
                return Response(response_data)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to GET /experiments list")

    def create(self, request):
        """
        POST: create a new experiment
        - canonical_number       - int
        - created_date           - string
        - description            - string
        - experiment_creator     - int
        - experiment_id          - int
        - experiment_members     - array of int
        - experiment_state       - string
        - is_canonical           - boolean
        - is_retired             - boolean
        - name                   - string
        - project_id             - int
        - resources              - array of int

        - description            - string
        - is_public              - bool
        - name                   - string

        Permission:
        - user is_project_creator
        - user is_project_member
        - user is_project_owner
        """
        try:
            project_id = request.data.get('project_id', None)
            if not project_id:
                raise ValidationError(
                    detail="project_id: must provide project_id")
            project = get_object_or_404(AerpawProject.objects.all(), pk=int(project_id))
            user = get_object_or_404(AerpawUser.objects.all(), pk=request.user.id)
        except Exception as exc:
            raise ValidationError(
                detail="ValidationError: {0}".format(exc))
        if project.is_creator(user) or project.is_member(user) or project.is_owner(user):
            # validate description
            description = request.data.get('description', None)
            if not description or len(description) < EXPERIMENT_MIN_DESC_LEN:
                raise ValidationError(
                    detail="description:  must be at least {0} chars long".format(EXPERIMENT_MIN_DESC_LEN))
            # validate experiment_state
            experiment_state = request.data.get('experiment_state', None)
            if experiment_state not in [c[0] for c in AerpawExperiment.ExperimentState.choices]:
                raise ValidationError(
                    detail="experiment_state: invalid value for experiment_state")
            # validate is_canonical
            is_canonical = str(request.data.get('is_canonical')).casefold() == 'true'
            # validate name
            name = request.data.get('name', None)
            if not name or len(name) < EXPERIMENT_MIN_NAME_LEN:
                raise ValidationError(
                    detail="name: must be at least {0} chars long".format(EXPERIMENT_MIN_NAME_LEN))
            # create project
            experiment = AerpawExperiment()
            experiment.created_by = user.username
            experiment.experiment_creator = user
            experiment.description = description
            experiment.experiment_state = experiment_state
            # TODO: update how is_canonical is determined
            experiment.is_canonical = is_canonical
            experiment.modified_by = user.username
            experiment.name = name
            experiment.project = project
            experiment.uuid = uuid4()
            # set canonical_number
            canonical_number = CanonicalNumber()
            canonical_number.canonical_number = get_current_canonical_number()
            increment_current_canonical_number()
            canonical_number.save()
            experiment.canonical_number = canonical_number
            experiment.save()
            # set creator as project_owner
            members = UserExperiment()
            members.granted_by = user
            members.experiment = experiment
            members.user = user
            members.save()
            return self.retrieve(request, pk=experiment.id)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to POST /experiments")

    def retrieve(self, request, *args, **kwargs):
        """
        GET: retrieve project as single result
        - canonical_number       - int
        - created_date           - string
        - description            - string
        - experiment_creator     - int
        - experiment_id          - int
        - experiment_members     - array of int
        - experiment_state       - string
        - is_canonical           - boolean
        - is_retired             - boolean
        - name                   - string
        - project_id             - int
        - resources              - array of int

        Permission:
        - user is_creator
        - user is_project_member
        - user is_project_owner
        - user is_operator
        """
        experiment = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
        project = get_object_or_404(AerpawProject.objects.all(), pk=experiment.project.id)
        if project.is_creator(request.user) or project.is_member(request.user) or \
                project.is_owner(request.user) or request.user.is_operator():
            serializer = ExperimentSerializerDetail(experiment)
            du = dict(serializer.data)
            experiment_members = []
            for p in du.get('experiment_members'):
                person = {
                    'granted_by': p.get('granted_by'),
                    'granted_date': str(p.get('granted_date')),
                    'user_id': p.get('user_id')
                }
                experiment_members.append(person)
            response_data = {
                'canonical_number': du.get('canonical_number'),
                'created_date': du.get('created_date'),
                'description': du.get('description'),
                'experiment_creator': du.get('experiment_creator'),
                'experiment_id': du.get('experiment_id'),
                'experiment_members': experiment_members,
                'experiment_state': du.get('experiment_state'),
                'is_canonical': du.get('is_canonical'),
                'is_retired': du.get('is_retired'),
                'last_modified_by': AerpawUser.objects.get(username=du.get('last_modified_by')).id,
                'modified_date': str(du.get('modified_date')),
                'name': du.get('name'),
                'project_id': du.get('project_id'),
                'resources': du.get('resources')
            }
            if experiment.is_deleted:
                response_data['is_deleted'] = du.get('is_deleted')
            return Response(response_data)
        else:
            raise PermissionDenied(
                detail="PermissionDenied: unable to GET /experiments/{0} details".format(kwargs.get('pk')))

    # def update(self, request, *args, **kwargs):
    #     """
    #     PUT: update existing project
    #     - description            - string
    #     - is_public              - bool
    #     - name                   - string
    #
    #     Permission:
    #     - user is_project_creator
    #     - user is_project_owner
    #     """
    #     project = get_object_or_404(AerpawProject.objects.all(), pk=kwargs.get('pk'))
    #     if not project.is_deleted and project.is_creator(request.user) or project.is_owner(request.user):
    #         modified = False
    #         # check for description
    #         if request.data.get('description', None):
    #             if len(request.data.get('description')) < PROJECT_MIN_DESC_LEN:
    #                 raise ValidationError(
    #                     detail="description:  must be at least {0} chars long".format(PROJECT_MIN_DESC_LEN))
    #             project.description = request.data.get('description')
    #             modified = True
    #         # check for is_public
    #         if str(request.data.get('is_public')).casefold() in ['true', 'false']:
    #             is_public = str(request.data.get('is_public')).casefold() == 'true'
    #             project.is_public = is_public
    #             modified = True
    #         # check for name
    #         if request.data.get('name', None):
    #             if len(request.data.get('name')) < PROJECT_MIN_NAME_LEN:
    #                 raise ValidationError(
    #                     detail="name: must be at least {0} chars long".format(PROJECT_MIN_NAME_LEN))
    #             project.name = request.data.get('name')
    #             modified = True
    #         # save if modified
    #         if modified:
    #             project.modified_by = request.user.email
    #             project.save()
    #         return self.retrieve(request, pk=project.id)
    #     else:
    #         raise PermissionDenied(
    #             detail="PermissionDenied: unable to PUT/PATCH /projects/{0} details".format(kwargs.get('pk')))
    #
    # def partial_update(self, request, *args, **kwargs):
    #     """
    #     PATCH: update existing project
    #     - description            - string
    #     - is_public              - bool
    #     - name                   - string
    #
    #     Permission:
    #     - user is_project_creator
    #     - user is_project_owner
    #     """
    #     return self.update(request, *args, **kwargs)
    #
    # def destroy(self, request, pk=None):
    #     """
    #     DELETE: soft delete existing project
    #     - is_deleted             - bool
    #
    #     Permission:
    #     - user is_project_creator
    #     """
    #     project = get_object_or_404(AerpawProject.objects.all(), pk=pk)
    #     if project.is_creator(request.user):
    #         project.is_deleted = True
    #         project.modified_by = request.user.username
    #         project.save()
    #         return Response(status=HTTP_204_NO_CONTENT)
    #     else:
    #         raise PermissionDenied(
    #             detail="PermissionDenied: unable to DELETE /projects/{0}".format(pk))
    #
    # @action(detail=True, methods=['get'])
    # def experiments(self, request, *args, **kwargs):
    #     """
    #     GET: experiments
    #     - description            - string
    #     - experiment_creator     - int
    #     - experiment_id          - int
    #     - experiment_state       - string
    #     - is_canonical           - boolean
    #     - is_retired             - boolean
    #     - name                   - string
    #
    #     Permission:
    #     - user is_project_creator
    #     - user is_project_member
    #     - user is_project_owner
    #     - user is_operator
    #     """
    #     project = get_object_or_404(AerpawProject.objects.all(), pk=kwargs.get('pk'))
    #     if project.is_creator(request.user) or project.is_member(request.user) or \
    #             project.is_owner(request.user) or request.user.is_operator():
    #         # TODO: experiments serializer and response
    #         response_data = {}
    #         return Response(response_data)
    #     else:
    #         raise PermissionDenied(
    #             detail="PermissionDenied: unable to GET /projects/{0}/experiments".format(kwargs.get('pk')))


# class UserProjectViewSet(GenericViewSet, RetrieveModelMixin, ListModelMixin, UpdateModelMixin):
#     """
#     UserProject
#     - paginated list
#     - retrieve one
#     """
#     permission_classes = [permissions.IsAuthenticated]
#     queryset = UserProject.objects.all().order_by('-granted_date')
#     serializer_class = UserProjectSerializer
#
#     def get_queryset(self):
#         project_id = self.request.query_params.get('project_id', None)
#         user_id = self.request.query_params.get('user_id', None)
#         if project_id and user_id:
#             queryset = UserProject.objects.filter(
#                 project__id=project_id,
#                 user__id=user_id
#             ).order_by('-granted_date')
#         elif project_id:
#             queryset = UserProject.objects.filter(
#                 project__id=project_id
#             ).order_by('-granted_date')
#         elif user_id:
#             queryset = UserProject.objects.filter(
#                 user__id=user_id
#             ).order_by('-granted_date')
#         else:
#             queryset = UserProject.objects.filter().order_by('-granted_date')
#         return queryset
#
#     def list(self, request, *args, **kwargs):
#         """
#         GET: list user-project as paginated results
#         - granted_by             - int
#         - granted_date           - string
#         - id                     - int
#         - project_id             - int
#         - project_role           - string
#         - user_id                - int
#
#         Permission:
#         - user is_operator
#         """
#         if request.user.is_operator():
#             page = self.paginate_queryset(self.get_queryset())
#             if page:
#                 serializer = UserProjectSerializer(page, many=True)
#             else:
#                 serializer = UserProjectSerializer(self.get_queryset(), many=True)
#             response_data = []
#             for u in serializer.data:
#                 du = dict(u)
#                 response_data.append(
#                     {
#                         'granted_by': du.get('granted_by'),
#                         'granted_date': du.get('granted_date'),
#                         'id': du.get('id'),
#                         'project_id': du.get('project_id'),
#                         'project_role': du.get('project_role'),
#                         'user_id': du.get('user_id')
#                     }
#                 )
#             if page:
#                 return self.get_paginated_response(response_data)
#             else:
#                 return Response(response_data)
#         else:
#             raise PermissionDenied(
#                 detail="PermissionDenied: unable to GET /user-project list")
#
#     def create(self, request):
#         """
#         POST: user cannot be created via the API
#         """
#         raise MethodNotAllowed(method="POST: /user-project")
#
#     def retrieve(self, request, *args, **kwargs):
#         """
#         GET: user-project as detailed result
#         - granted_by             - int
#         - granted_date           - string
#         - id                     - int
#         - project_id             - int
#         - project_role           - string
#         - user_id                - int
#
#         Permission:
#         - user is_operator
#         """
#         user_project = get_object_or_404(self.queryset, pk=kwargs.get('pk'))
#         if request.user.is_operator():
#             serializer = UserProjectSerializer(user_project)
#             du = dict(serializer.data)
#             response_data = {
#                 'granted_by': du.get('granted_by'),
#                 'granted_date': du.get('granted_date'),
#                 'id': du.get('id'),
#                 'project_id': du.get('project_id'),
#                 'project_role': du.get('project_role'),
#                 'user_id': du.get('user_id')
#             }
#             return Response(response_data)
#         else:
#             raise PermissionDenied(
#                 detail="PermissionDenied: unable to GET /user-project/{0} details".format(kwargs.get('pk')))
#
#     def update(self, request, *args, **kwargs):
#         """
#         PUT: user-project cannot be updated via the API
#         """
#         raise MethodNotAllowed(method="PUT/PATCH: /user-project/{user_id}")
#
#     def partial_update(self, request, *args, **kwargs):
#         """
#         PATCH: user-project cannot be updated via the API
#         """
#         return self.update(request, *args, **kwargs)
#
#     def destroy(self, request, pk=None):
#         """
#         DELETE: user-project cannot be deleted via the API
#         """
#         raise MethodNotAllowed(method="DELETE: /user-project/{user_id}")
