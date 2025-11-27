from django.contrib.auth.models import AbstractUser
from django.db import models


class AdminUser(AbstractUser):
    """
    Modelo customizado de usuário para administradores do sistema.
    Estende o AbstractUser do Django para aproveitar toda funcionalidade de autenticação.
    """
    
    class Meta:
        db_table = 'admin_users'
        verbose_name = 'Usuário Administrador'
        verbose_name_plural = 'Usuários Administradores'
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.username
