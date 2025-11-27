from django.contrib import admin
from .models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """
    Configuração do admin para Ticket.
    """
    list_display = ['codigo_ticket', 'cliente_nome', 'demanda', 'status', 'criado_em', 'finalizado_em']
    list_filter = ['status', 'demanda', 'criado_em']
    search_fields = ['codigo_ticket', 'cliente_nome', 'demanda__concurso']
    ordering = ['criado_em']
    date_hierarchy = 'criado_em'
    readonly_fields = ['codigo_ticket', 'criado_em', 'posicao_fila']
    
    fieldsets = (
        ('Informações do Ticket', {
            'fields': ('codigo_ticket', 'demanda', 'cliente_nome', 'status')
        }),
        ('Posicionamento', {
            'fields': ('posicao_fila',)
        }),
        ('Datas', {
            'fields': ('criado_em', 'finalizado_em')
        }),
    )
    
    def posicao_fila(self, obj):
        """Exibe a posição na fila no admin."""
        posicao = obj.posicao_fila
        return posicao if posicao else '-'
    posicao_fila.short_description = 'Posição na Fila'
