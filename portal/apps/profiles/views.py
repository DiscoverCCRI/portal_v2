# import files
import tempfile, os, subprocess
from zipfile import ZipFile

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import FileResponse

from portal.apps.profiles.models import update_credential
from portal.apps.profiles.forms import DiscoverUserCredentialForm
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

@login_required
def credential(request):
    """
    :param request:
    :return:
    """

    if request.method == "POST":
        form = DiscoverUserCredentialForm(request.POST)
        if 'savebtn' in request.POST and form.is_valid():
            if request.POST['publickey'] and request.POST['note']:
                update_credential(request, form)
                form = DiscoverUserCredentialForm()  # clear form
            render(request, 'credential.html', {'form': form})

        elif 'generatebtn' in request.POST:
            keyfile = os.path.join(tempfile.gettempdir(), 'aerpaw_id_rsa')
            args = "ssh-keygen -q -t rsa -N '' -C {} -f {}".format(request.user.username,
                                                                   keyfile).split()
            args[5] = ''  # make passphrase empty (the parameter for -N)
            try:
                output = subprocess.run(args, check=False, capture_output=True)
                with ZipFile(os.path.join(tempfile.gettempdir(), 'aerpaw_id_rsa.zip'),
                             'w') as myzip:
                    myzip.write(keyfile + '.pub', arcname='aerpaw_id_rsa.pub')
                    myzip.write(keyfile, arcname='aerpaw_id_rsa')
                os.unlink(keyfile)
                os.unlink(keyfile + '.pub')
                return FileResponse(
                    open(os.path.join(tempfile.gettempdir(), 'aerpaw_id_rsa.zip'), 'rb'),
                    as_attachment=True)
            except Exception as e:
                print(e)
    else:
        form = DiscoverUserCredentialForm()

    return render(request, 'credential.html', { 'form': form })