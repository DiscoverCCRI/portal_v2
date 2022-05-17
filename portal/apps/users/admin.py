from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# from .forms import AerpawUserCreationForm, AerpawUserChangeForm
from .models import AerpawUser


class AerpawUserAdmin(UserAdmin):
    # add_form = AerpawUserCreationForm
    # form = AerpawUserChangeForm
    model = AerpawUser
    list_display = ["email", "username",]


admin.site.register(AerpawUser, AerpawUserAdmin)
