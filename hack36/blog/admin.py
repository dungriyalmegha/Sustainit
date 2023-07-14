

from django.contrib import admin

# Register your models here.
# admin.py

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

admin.site.unregister(User)
admin.site.register(User, UserAdmin)


