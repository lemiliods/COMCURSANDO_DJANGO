from django.contrib import admin
from django.utils.html import format_html
from .models import Demanda


@admin.register(Demanda)
class DemandaAdmin(admin.ModelAdmin):
    """
    Configuração do admin para Demanda.
    """
    list_display = ['concurso_formatado', 'numero_edital', 'banca', 'cargo', 'valor_badge', 'data_concurso', 'status_badge', 'total_tickets', 'criado_em']
    list_filter = ['status', 'banca', 'data_concurso', 'criado_em']
    search_fields = ['concurso', 'numero_edital', 'cargo', 'autarquia', 'banca']
    ordering = ['-criado_em']
    date_hierarchy = 'criado_em'
    list_per_page = 20
    
    fieldsets = (
        ('📋 Informações do Concurso', {
            'fields': ('concurso', 'numero_edital', 'banca'),
            'description': 'Dados principais do concurso público'
        }),
        ('👥 Detalhes do Cargo', {
            'fields': ('cargo', 'autarquia')
        }),
        ('💰 Recompensa', {
            'fields': ('valor_recompensa',),
            'description': 'Valor a pagar por prova aprovada (em Reais)'
        }),
        ('📅 Agendamento e Status', {
            'fields': ('data_concurso', 'status')
        }),
        ('🕐 Registro', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['criado_em', 'atualizado_em']
    
    def concurso_formatado(self, obj):
        """Exibe o concurso em negrito."""
        return format_html('<strong>{}</strong>', obj.concurso)
    concurso_formatado.short_description = 'Concurso'
    concurso_formatado.admin_order_field = 'concurso'
    
    def status_badge(self, obj):
        """Exibe badge colorido do status."""
        cores = {
            'aberto': '#28a745',
            'em_andamento': '#ffc107',
            'encerrado': '#dc3545',
            'cancelado': '#6c757d'
        }
        cor = cores.get(obj.status, '#007bff')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            cor, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def valor_badge(self, obj):
        """Exibe o valor da recompensa."""
        if obj.valor_recompensa:
            return format_html(
                '<span style="color: #28a745; font-weight: bold; font-size: 13px;">R$ {}</span>',
                obj.valor_recompensa
            )
        return format_html('<span style="color: #6c757d;">-</span>')
    valor_badge.short_description = 'Recompensa'
    valor_badge.admin_order_field = 'valor_recompensa'
    
    def total_tickets(self, obj):
        """Exibe total de tickets associados."""
        if obj.pk:  # Só conta se já foi salvo
            total = obj.tickets.count()
            if total > 0:
                return format_html('<span style="color: #007bff; font-weight: bold;">{} ticket(s)</span>', total)
        return format_html('<span style="color: #6c757d;">Nenhum</span>')
    total_tickets.short_description = 'Tickets'
