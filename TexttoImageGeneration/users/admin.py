from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserRegistrationModel

# Register your models here.
class um(admin.ModelAdmin):
    list_display = ('name', 'loginid', 'password', 'mobile', 'email', 'status')

admin.site.register(UserRegistrationModel, um)