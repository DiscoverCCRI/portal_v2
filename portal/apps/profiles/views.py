from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from portal.apps.users.api.viewsets import UserViewSet
from portal.apps.users.oidc_users import get_tokens_for_user, refresh_access_token_for_user


@login_required
def profile(request):
    """
    :param request:
    :return:
    """
    user = request.user
    user_data = UserViewSet()
    if request.method == 'POST':
        if request.POST.get('display_name') and len(request.POST.get('display_name')) >= 3:
            request.data = {'display_name': request.POST.get('display_name')}
            user_data.update(request, pk=user.id)
        if request.POST.get('authorization_token'):
            get_tokens_for_user(user)
        if request.POST.get('refresh_access_token'):
            refresh_access_token_for_user(user)

    return render(request, 'profile.html', {'user': user, 'user_data': user_data.retrieve(request, pk=user.id).data})
