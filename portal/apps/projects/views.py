from urllib.parse import parse_qs, urlparse

from django.contrib.auth.decorators import login_required
from django.http import QueryDict
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from portal.apps.projects.api.viewsets import ProjectViewSet
from portal.apps.projects.forms import ProjectCreateForm, ProjectMembershipForm
from portal.apps.projects.models import AerpawProject
from portal.server.settings import REST_FRAMEWORK


@csrf_exempt
@login_required
def project_list(request):
    message = None
    # TODO: request to join project
    try:
        # check for query parameters
        current_page = 1
        search_term = None
        data_dict = {}
        if request.GET.get('search'):
            data_dict['search'] = request.GET.get('search')
            search_term = request.GET.get('search')
        if request.GET.get('page'):
            data_dict['page'] = request.GET.get('page')
            current_page = int(request.GET.get('page'))
        request.query_params = QueryDict('', mutable=True)
        request.query_params.update(data_dict)
        p = ProjectViewSet(request=request)
        projects = p.list(request=request)
        # get prev, next and item range
        next_page = None
        prev_page = None
        count = 0
        min_range = 0
        max_range = 0
        if projects.data:
            prev_url = projects.data.get('previous', None)
            if prev_url:
                prev_dict = parse_qs(urlparse(prev_url).query)
                try:
                    prev_page = prev_dict['page'][0]
                except Exception as exc:
                    print(exc)
                    prev_page = 1
            next_url = projects.data.get('next', None)
            if next_url:
                next_dict = parse_qs(urlparse(next_url).query)
                try:
                    next_page = next_dict['page'][0]
                except Exception as exc:
                    print(exc)
                    next_page = 1
            count = int(projects.data.get('count'))
            min_range = int(current_page - 1) * int(REST_FRAMEWORK['PAGE_SIZE']) + 1
            max_range = int(current_page - 1) * int(REST_FRAMEWORK['PAGE_SIZE']) + int(REST_FRAMEWORK['PAGE_SIZE'])
            if max_range > count:
                max_range = count

        item_range = '{0} - {1}'.format(str(min_range), str(max_range))
    except Exception as exc:
        message = exc
        projects = None
        item_range = None
        next_page = None
        prev_page = None
        search_term = None
        count = 0
    return render(request,
                  'project_list.html',
                  {
                      'user': request.user,
                      'projects': projects,
                      'item_range': item_range,
                      'message': message,
                      'next_page': next_page,
                      'prev_page': prev_page,
                      'search': search_term,
                      'count': count
                  })


@csrf_exempt
@login_required
def project_detail(request, project_id):
    p = ProjectViewSet(request=request)
    message = None
    try:
        if request.method == "POST":
            if request.POST.get('delete-project') == "true":
                project = p.destroy(request=request, pk=project_id).data
                return redirect('project_list')
        project = p.retrieve(request=request, pk=project_id).data
        if project.get('membership').get('is_project_creator') or project.get('membership').get('is_project_owner') or \
                project.get('membership').get('is_project_member'):
            experiments = p.experiments(request=request, pk=project_id).data
        else:
            experiments = None
    except Exception as exc:
        message = exc
        project = None
        experiments = None
    return render(request,
                  'project_detail.html',
                  {
                      'user': request.user,
                      'project': project,
                      'experiments': experiments,
                      'message': message
                  })


@csrf_exempt
@login_required
def project_create(request):
    message = None
    if request.method == "POST":
        form = ProjectCreateForm(request.POST)
        if form.is_valid():
            try:
                request.data = QueryDict('', mutable=True)
                data_dict = form.data.dict()
                if data_dict.get('is_public', '') == 'on':
                    data_dict.update({'is_public': 'true'})
                else:
                    data_dict.update({'is_public': 'false'})
                request.data.update(data_dict)
                p = ProjectViewSet(request=request)
                request.data.update(data_dict)
                project = p.create(request=request).data
                return redirect('project_detail', project_id=project.get('project_id', 9999))
            except Exception as exc:
                message = exc
    else:
        form = ProjectCreateForm()
    return render(request,
                  'project_create.html',
                  {
                      'form': form,
                      'message': message
                  })


@csrf_exempt
@login_required
def project_edit(request, project_id):
    message = None
    if request.method == "POST":
        form = ProjectCreateForm(request.POST)
        if form.is_valid():
            try:
                request.data = QueryDict('', mutable=True)
                data_dict = form.data.dict()
                if data_dict.get('is_active', '') == 'on':
                    data_dict.update({'is_active': 'true'})
                else:
                    data_dict.update({'is_active': 'false'})
                request.data.update(data_dict)
                p = ProjectViewSet(request=request)
                request.data.update(data_dict)
                project = p.partial_update(request=request, pk=project_id)
                return redirect('project_detail', project_id=project_id)
            except Exception as exc:
                message = exc
    else:
        project = get_object_or_404(AerpawProject, id=project_id)
        is_project_creator = project.is_creator(request.user)
        is_project_owner = project.is_owner(request.user)
        form = ProjectCreateForm(instance=project)
    return render(request,
                  'project_edit.html',
                  {
                      'form': form,
                      'message': message,
                      'project_id': project_id,
                      'is_project_creator': is_project_creator,
                      'is_project_owner': is_project_owner
                  })


@csrf_exempt
@login_required
def project_members(request, project_id):
    message = None
    is_project_creator = False
    is_project_owner = False
    if request.method == "POST":
        form = ProjectMembershipForm(request.POST)
        if form.is_valid():
            try:
                request.query_params = QueryDict('', mutable=True)
                request.data = QueryDict('', mutable=True)
                request.data.setlist('project_members', [int(i) for i in request.POST.getlist('project_members')])
                p = ProjectViewSet(request=request)
                project = p.membership(request=request, pk=project_id)
                return redirect('project_detail', project_id=project_id)
            except Exception as exc:
                message = exc
    else:
        project = get_object_or_404(AerpawProject, id=project_id)
        is_project_creator = project.is_creator(request.user)
        is_project_owner = project.is_owner(request.user)
        initial_dict = {
            'project_members': list(project.project_members())
        }
        form = ProjectMembershipForm(instance=project, initial=initial_dict)
    return render(request,
                  'project_members.html',
                  {
                      'form': form,
                      'message': message,
                      'project_id': project_id,
                      'is_project_creator': is_project_creator,
                      'is_project_owner': is_project_owner
                  })


@csrf_exempt
@login_required
def project_owners(request, project_id):
    message = None
    is_project_creator = False
    is_project_owner = False
    if request.method == "POST":
        form = ProjectMembershipForm(request.POST)
        if form.is_valid():
            try:
                request.query_params = QueryDict('', mutable=True)
                request.data = QueryDict('', mutable=True)
                request.data.setlist('project_owners', [int(i) for i in request.POST.getlist('project_owners')])
                p = ProjectViewSet(request=request)
                project = p.membership(request=request, pk=project_id)
                return redirect('project_detail', project_id=project_id)
            except Exception as exc:
                message = exc
    else:
        project = get_object_or_404(AerpawProject, id=project_id)
        is_project_creator = project.is_creator(request.user)
        is_project_owner = project.is_owner(request.user)
        initial_dict = {
            'project_owners': list(project.project_owners())
        }
        form = ProjectMembershipForm(instance=project, initial=initial_dict)
    return render(request,
                  'project_owners.html',
                  {
                      'form': form,
                      'message': message,
                      'project_id': project_id,
                      'is_project_creator': is_project_creator,
                      'is_project_owner': is_project_owner
                  })
