from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import AdminUser


@admin.register(AdminUser)
class AdminUserAdmin(UserAdmin):
    """
    Configuração do admin para AdminUser.
    """
    list_display = ['username', 'email', 'nome_completo', 'status_badge', 'tipo_usuario', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    list_per_page = 20
    
    fieldsets = (
        ('Credenciais', {
            'fields': ('username', 'password')
        }),
        ('Informações Pessoais', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Permissões', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Datas Importantes', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    def nome_completo(self, obj):
        """Exibe o nome completo do usuário."""
        return f"{obj.first_name} {obj.last_name}" if obj.first_name or obj.last_name else '-'
    nome_completo.short_description = 'Nome Completo'
    
    def status_badge(self, obj):
        """Exibe badge colorido do status."""
        if obj.is_active:
            return format_html('<span style="color: green; font-weight: bold;">● Ativo</span>')
        return format_html('<span style="color: red; font-weight: bold;">● Inativo</span>')
    status_badge.short_description = 'Status'
    
    def tipo_usuario(self, obj):
        """Exibe o tipo de usuário."""
        if obj.is_superuser:
            return format_html('<span style="color: #dc3545; font-weight: bold;">Superusuário</span>')
        elif obj.is_staff:
            return format_html('<span style="color: #007bff; font-weight: bold;">Staff</span>')
        return format_html('<span style="color: #6c757d;">Usuário</span>')
    tipo_usuario.short_description = 'Tipo'
