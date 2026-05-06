from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Branch, User

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Branch', {'fields': ('branch',)}),
    )

admin.site.register(Branch)
admin.site.register(User, CustomUserAdmin)
