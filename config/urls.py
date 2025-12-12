"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from apps.users.views import login_view, AdminUserViewSet
from apps.concursos.views import DemandaViewSet
from apps.concursos.views_public import home_view
from apps.tickets.views import TicketViewSet
from apps.tickets.views_public import ticket_novo_view, ticket_success_view, ticket_upload_view
from config.admin import admin_site

# Registrar modelos no admin customizado
from apps.users.admin import AdminUserAdmin
from apps.concursos.admin import DemandaAdmin
from apps.tickets.admin import TicketAdmin
from apps.users.models import AdminUser
from apps.concursos.models import Demanda
from apps.tickets.models import Ticket

admin_site.register(AdminUser, AdminUserAdmin)
admin_site.register(Demanda, DemandaAdmin)
admin_site.register(Ticket, TicketAdmin)

# Router do Django REST Framework
router = DefaultRouter()
router.register(r'users', AdminUserViewSet, basename='user')
router.register(r'demandas', DemandaViewSet, basename='demanda')
router.register(r'tickets', TicketViewSet, basename='ticket')

urlpatterns = [
    path('', home_view, name='home'),  # Página pública
    path('ticket/novo/<int:demanda_id>/', ticket_novo_view, name='ticket_novo'),
    path('ticket/sucesso/<int:ticket_id>/', ticket_success_view, name='ticket_success'),
    path('ticket/upload/<int:ticket_id>/', ticket_upload_view, name='ticket_upload'),
    path('admin/', admin_site.urls),  # Usando admin customizado
    path('api/auth/login', login_view, name='login'),
    path('api/', include(router.urls)),
]

# Servir arquivos de media em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
