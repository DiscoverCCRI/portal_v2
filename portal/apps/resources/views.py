from urllib.parse import parse_qs, urlparse

from django.contrib.auth.decorators import login_required
from django.http import QueryDict
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from portal.apps.resources.api.viewsets import ResourceViewSet
from portal.apps.resources.forms import ResourceCreateForm
from portal.apps.resources.models import AerpawResource
from portal.server.settings import REST_FRAMEWORK


@csrf_exempt
@login_required
def resource_list(request):
    message = None
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
        r = ResourceViewSet(request=request)
        resources = r.list(request=request)
        # get prev, next and item range
        next_page = None
        prev_page = None
        count = 0
        min_range = 0
        max_range = 0
        if resources.data:
            prev_url = resources.data.get('previous', None)
            if prev_url:
                prev_dict = parse_qs(urlparse(prev_url).query)
                try:
                    prev_page = prev_dict['page'][0]
                except Exception as exc:
                    print(exc)
                    prev_page = 1
            next_url = resources.data.get('next', None)
            if next_url:
                next_dict = parse_qs(urlparse(next_url).query)
                try:
                    next_page = next_dict['page'][0]
                except Exception as exc:
                    print(exc)
                    next_page = 1
            count = int(resources.data.get('count'))
            min_range = int(current_page - 1) * int(REST_FRAMEWORK['PAGE_SIZE']) + 1
            max_range = int(current_page - 1) * int(REST_FRAMEWORK['PAGE_SIZE']) + int(REST_FRAMEWORK['PAGE_SIZE'])
            if max_range > count:
                max_range = count

        item_range = '{0} - {1}'.format(str(min_range), str(max_range))
    except Exception as exc:
        message = exc
        resources = None
        item_range = None
        next_page = None
        prev_page = None
        search_term = None
        count = 0
    return render(request,
                  'resource_list.html',
                  {
                      'user': request.user,
                      'resources': resources,
                      'item_range': item_range,
                      'message': message,
                      'next_page': next_page,
                      'prev_page': prev_page,
                      'search': search_term,
                      'count': count
                  })


@csrf_exempt
@login_required
def resource_detail(request, resource_id):
    r = ResourceViewSet(request=request)
    message = None
    try:
        if request.method == "POST":
            if request.POST.get('delete-resource') == "true":
                resource = r.destroy(request=request, pk=resource_id).data
                return redirect('resource_list')
        resource = r.retrieve(request=request, pk=resource_id).data
    except Exception as exc:
        message = exc
        resource = None
    return render(request,
                  'resource_detail.html',
                  {
                      'user': request.user,
                      'resource': resource,
                      'message': message
                  })


@csrf_exempt
@login_required
def resource_create(request):
    message = None
    if request.method == "POST":
        form = ResourceCreateForm(request.POST)
        if form.is_valid():
            try:
                request.data = QueryDict('', mutable=True)
                data_dict = form.data.dict()
                if data_dict.get('is_active', '') == 'on':
                    data_dict.update({'is_active': 'true'})
                else:
                    data_dict.update({'is_active': 'false'})
                request.data.update(data_dict)
                r = ResourceViewSet(request=request)
                request.data.update(data_dict)
                resource = r.create(request=request).data
                return redirect('resource_detail', resource_id=resource.get('resource_id', 9999))
            except Exception as exc:
                message = exc
    else:
        form = ResourceCreateForm()
    return render(request,
                  'resource_create.html',
                  {
                      'form': form,
                      'message': message
                  })


@csrf_exempt
@login_required
def resource_edit(request, resource_id):
    message = None
    if request.method == "POST":
        form = ResourceCreateForm(request.POST)
        if form.is_valid():
            try:
                request.data = QueryDict('', mutable=True)
                data_dict = form.data.dict()
                if data_dict.get('is_active', '') == 'on':
                    data_dict.update({'is_active': 'true'})
                else:
                    data_dict.update({'is_active': 'false'})
                request.data.update(data_dict)
                r = ResourceViewSet(request=request)
                request.data.update(data_dict)
                resource = r.partial_update(request=request, pk=resource_id)
                return redirect('resource_detail', resource_id=resource_id)
            except Exception as exc:
                message = exc
    else:
        resource = get_object_or_404(AerpawResource, id=resource_id)
        form = ResourceCreateForm(instance=resource)
    return render(request,
                  'resource_edit.html',
                  {
                      'form': form,
                      'message': message,
                      'resource_id': resource_id
                  })
