from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
admin.site.register(User, UserAdmin)
admin.site.site_header = "Portal • Administração de pessoas"
admin.site.site_title = "Portal"
