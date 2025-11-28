from django.contrib import admin
from django.utils.html import format_html
from .models import Demanda
import logging

logger = logging.getLogger(__name__)


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
    
    def changelist_view(self, request, extra_context=None):
        """Override para adicionar logging e capturar erros."""
        try:
            logger.info(f"Acessando changelist_view para Demanda - User: {request.user}")
            return super().changelist_view(request, extra_context)
        except Exception as e:
            logger.error(f"ERRO no changelist_view: {type(e).__name__}: {str(e)}", exc_info=True)
            raise
    
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
        try:
            return format_html('<strong>{}</strong>', obj.concurso)
        except Exception as e:
            logger.error(f"Erro em concurso_formatado: {e}", exc_info=True)
            return "Erro"
    concurso_formatado.short_description = 'Concurso'
    concurso_formatado.admin_order_field = 'concurso'
    
    def status_badge(self, obj):
        """Exibe badge colorido do status."""
        try:
            cores = {
                'aberto': '#28a745',
                'em_analise': '#ffc107',
                'concluido': '#007bff',
                'cancelado': '#6c757d'
            }
            cor = cores.get(obj.status, '#007bff')
            return format_html(
                '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
                cor, obj.get_status_display()
            )
        except Exception as e:
            logger.error(f"Erro em status_badge: {e}", exc_info=True)
            return "Erro"
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def valor_badge(self, obj):
        """Exibe o valor da recompensa."""
        try:
            valor = obj.valor_recompensa if obj.valor_recompensa is not None else 50.00
            valor_formatado = f"R$ {float(valor):.2f}"
            return format_html(
                '<span style="color: #28a745; font-weight: bold; font-size: 13px;">{}</span>',
                valor_formatado
            )
        except Exception as e:
            logger.error(f"Erro em valor_badge - ID: {obj.id}: {e}", exc_info=True)
            return format_html('<span style="color: #6c757d;">R$ 50.00</span>')
    valor_badge.short_description = 'Recompensa'
    valor_badge.admin_order_field = 'valor_recompensa'
    
    def total_tickets(self, obj):
        """Exibe total de tickets associados."""
        try:
            if obj.pk:  # Só conta se já foi salvo
                total = obj.tickets.count()
                if total > 0:
                    return format_html('<span style="color: #007bff; font-weight: bold;">{} envio(s)</span>', total)
        except (AttributeError, ValueError):
            pass
        return format_html('<span style="color: #6c757d;">Nenhum</span>')
    total_tickets.short_description = 'Envios'
