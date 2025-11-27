from django.contrib import admin
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta


class CustomAdminSite(admin.AdminSite):
    """
    Site admin customizado com dashboard profissional.
    """
    
    def index(self, request, extra_context=None):
        """
        Override do index para adicionar estatísticas ao dashboard.
        """
        from apps.tickets.models import Ticket
        from apps.concursos.models import Demanda
        from apps.users.models import AdminUser
        
        # Estatísticas de tickets
        total_tickets = Ticket.objects.count()
        tickets_aguardando = Ticket.objects.filter(status='aguardando').count()
        tickets_atendendo = Ticket.objects.filter(status='atendendo').count()
        tickets_finalizados = Ticket.objects.filter(status='finalizado').count()
        
        # Tickets criados hoje
        hoje = timezone.now().date()
        tickets_hoje = Ticket.objects.filter(criado_em__date=hoje).count()
        
        # Percentuais
        if total_tickets > 0:
            percent_aguardando = round((tickets_aguardando / total_tickets) * 100, 1)
            percent_atendendo = round((tickets_atendendo / total_tickets) * 100, 1)
            percent_finalizados = round((tickets_finalizados / total_tickets) * 100, 1)
        else:
            percent_aguardando = percent_atendendo = percent_finalizados = 0
        
        # Concursos
        concursos_abertos = Demanda.objects.filter(status='aberto').count()
        
        # Usuários
        usuarios_ativos = AdminUser.objects.filter(is_active=True).count()
        
        # Últimos tickets
        ultimos_tickets = Ticket.objects.select_related('demanda').order_by('-criado_em')[:5]
        
        # Top demandas (com mais tickets)
        top_demandas = Demanda.objects.annotate(
            total_tickets=Count('tickets')
        ).order_by('-total_tickets')[:5]
        
        extra_context = extra_context or {}
        extra_context.update({
            'total_tickets': total_tickets,
            'tickets_aguardando': tickets_aguardando,
            'tickets_atendendo': tickets_atendendo,
            'tickets_finalizados': tickets_finalizados,
            'tickets_hoje': tickets_hoje,
            'percent_aguardando': percent_aguardando,
            'percent_atendendo': percent_atendendo,
            'percent_finalizados': percent_finalizados,
            'concursos_abertos': concursos_abertos,
            'usuarios_ativos': usuarios_ativos,
            'ultimos_tickets': ultimos_tickets,
            'top_demandas': top_demandas,
        })
        
        return super().index(request, extra_context)


# Instância do site admin customizado
admin_site = CustomAdminSite(name='admin')
