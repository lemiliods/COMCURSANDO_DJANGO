from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from django.utils import timezone
from .models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """
    Configuração do admin para Envios de Prova.
    """
    list_display = ['codigo_ticket_formatado', 'cliente_nome', 'concurso_info', 'pix_info', 'status_badge', 'arquivo_preview', 'valor_info', 'criado_em']
    list_filter = ['status', 'demanda__banca', 'criado_em', 'analisado_em', 'pago_em']
    search_fields = ['codigo_ticket', 'cliente_nome', 'cliente_pix', 'demanda__concurso', 'demanda__numero_edital']
    ordering = ['-criado_em']
    date_hierarchy = 'criado_em'
    readonly_fields = ['codigo_ticket', 'criado_em', 'atualizado_em', 'analisado_em', 'pago_em']
    list_per_page = 25
    actions = ['aprovar_prova', 'recusar_prova', 'marcar_como_pago']
    
    fieldsets = (
        ('📄 Informações do Envio', {
            'fields': ('codigo_ticket', 'demanda', 'cliente_nome', 'cliente_pix'),
            'description': 'Dados do cliente e do envio'
        }),
        ('📎 Arquivo da Prova', {
            'fields': ('arquivo_prova',)
        }),
        ('📊 Análise e Pagamento', {
            'fields': ('status', 'observacoes_admin', 'valor_pago')
        }),
        ('⏱️ Timestamps', {
            'fields': ('criado_em', 'analisado_em', 'pago_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
    
    def codigo_ticket_formatado(self, obj):
        """Exibe o código do envio em destaque."""
        return format_html(
            '<span style="font-family: monospace; font-size: 13px; font-weight: bold; color: #495057; background: #f8f9fa; padding: 4px 8px; border-radius: 3px;">{}</span>',
            obj.codigo_ticket
        )
    codigo_ticket_formatado.short_description = 'Código'
    codigo_ticket_formatado.admin_order_field = 'codigo_ticket'
    
    def concurso_info(self, obj):
        """Exibe informações do concurso associado."""
        return format_html(
            '<div style="line-height: 1.4;"><strong>{}</strong><br><small style="color: #6c757d;">Edital: {} | {}</small></div>',
            obj.demanda.concurso,
            obj.demanda.numero_edital,
            obj.demanda.cargo
        )
    concurso_info.short_description = 'Concurso'
    
    def pix_info(self, obj):
        """Exibe a chave PIX."""
        return format_html(
            '<span style="font-family: monospace; font-size: 12px; background: #e8f5e9; color: #2e7d32; padding: 4px 8px; border-radius: 3px;">{}</span>',
            obj.cliente_pix
        )
    pix_info.short_description = 'Chave PIX'
    
    def arquivo_preview(self, obj):
        """Exibe preview/link do arquivo."""
        if obj.arquivo_prova:
            return format_html(
                '<a href="{}" target="_blank" style="background: #007bff; color: white; padding: 4px 12px; border-radius: 4px; text-decoration: none; font-size: 11px;">📄 Ver Prova</a>',
                obj.arquivo_prova.url
            )
        return format_html('<span style="color: #6c757d;">-</span>')
    arquivo_preview.short_description = 'Arquivo'
    
    def valor_info(self, obj):
        """Exibe informações de valor."""
        if obj.valor_pago:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">R$ {}</span>',
                obj.valor_pago
            )
        elif obj.demanda.valor_recompensa:
            return format_html(
                '<span style="color: #6c757d;">R$ {}</span>',
                obj.demanda.valor_recompensa
            )
        return '-'
    valor_info.short_description = 'Valor'
    
    def status_badge(self, obj):
        """Exibe badge colorido do status."""
        cores = {
            'aguardando': '#17a2b8',
            'em_analise': '#ffc107',
            'aprovado': '#28a745',
            'pago': '#155724',
            'recusado': '#dc3545'
        }
        cor = cores.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: bold; text-transform: uppercase;">{}</span>',
            cor, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    # Actions personalizadas
    def aprovar_prova(self, request, queryset):
        """Aprova provas selecionadas."""
        count = 0
        for ticket in queryset:
            if ticket.status in ['aguardando', 'em_analise']:
                ticket.status = 'aprovado'
                ticket.analisado_em = timezone.now()
                ticket.save()
                count += 1
        self.message_user(request, f'{count} prova(s) aprovada(s). Agora marque como PAGO após enviar o PIX.')
    aprovar_prova.short_description = '✓ Aprovar Prova'
    
    def recusar_prova(self, request, queryset):
        """Recusa provas selecionadas."""
        count = 0
        for ticket in queryset:
            if ticket.status in ['aguardando', 'em_analise']:
                ticket.status = 'recusado'
                ticket.analisado_em = timezone.now()
                # Retornar demanda para aberto
                ticket.demanda.status = 'aberto'
                ticket.demanda.save()
                ticket.save()
                count += 1
        self.message_user(request, f'{count} prova(s) recusada(s). Demanda(s) voltaram para "aberto".')
    recusar_prova.short_description = '✗ Recusar Prova'
    
    def marcar_como_pago(self, request, queryset):
        """Marca provas aprovadas como pagas."""
        count = 0
        for ticket in queryset:
            if ticket.status == 'aprovado':
                ticket.status = 'pago'
                ticket.pago_em = timezone.now()
                if not ticket.valor_pago:
                    ticket.valor_pago = ticket.demanda.valor_recompensa
                # Marcar demanda como concluída
                ticket.demanda.status = 'concluido'
                ticket.demanda.save()
                ticket.save()
                count += 1
        self.message_user(request, f'{count} prova(s) marcada(s) como PAGA.')
    marcar_como_pago.short_description = '💰 Marcar como Pago'
