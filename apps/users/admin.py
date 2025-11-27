from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import AdminUser


@admin.register(AdminUser)
class AdminUserAdmin(UserAdmin):
    """
    Configuração do admin para AdminUser.
    """
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
