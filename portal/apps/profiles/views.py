from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from portal.apps.users.api.viewsets import UserViewSet
from portal.apps.users.oidc_users import get_tokens_for_user, refresh_access_token_for_user
from portal.server.settings import DEBUG


@csrf_exempt
@login_required
def profile(request):
    """
    :param request:
    :return:
    """
    message = None
    user = request.user
    user_data = UserViewSet()
    if request.method == 'POST':
        try:
            if request.POST.get('display_name'):
                request.data = {'display_name': request.POST.get('display_name')}
                user_data.update(request, pk=user.id)
            if request.POST.get('authorization_token'):
                get_tokens_for_user(user)
            if request.POST.get('refresh_access_token'):
                refresh_access_token_for_user(user)
        except Exception as exc:
            message = exc
    return render(request,
                  'profile.html',
                  {
                      'user': user,
                      'user_data': user_data.retrieve(request=request, pk=request.user.id).data,
                      'user_tokens': user_data.tokens(request=request, pk=request.user.id).data,
                      'message': message,
                      'debug': DEBUG
                  })
