from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """
    Configuração do admin para Ticket.
    """
    list_display = ['codigo_ticket_formatado', 'cliente_nome', 'concurso_info', 'status_badge', 'posicao_fila_badge', 'tempo_espera', 'criado_em']
    list_filter = ['status', 'demanda__banca', 'demanda__status', 'criado_em']
    search_fields = ['codigo_ticket', 'cliente_nome', 'demanda__concurso', 'demanda__numero_edital']
    ordering = ['criado_em']
    date_hierarchy = 'criado_em'
    readonly_fields = ['codigo_ticket', 'criado_em', 'atualizado_em', 'posicao_fila_detalhada', 'tempo_total']
    list_per_page = 25
    actions = ['marcar_como_atendendo', 'marcar_como_finalizado', 'marcar_como_cancelado']
    
    fieldsets = (
        ('🎫 Informações do Ticket', {
            'fields': ('codigo_ticket', 'demanda', 'cliente_nome'),
            'description': 'Dados principais do ticket'
        }),
        ('📊 Status e Posição', {
            'fields': ('status', 'posicao_fila_detalhada')
        }),
        ('⏱️ Temporização', {
            'fields': ('criado_em', 'finalizado_em', 'tempo_total'),
            'classes': ('collapse',)
        }),
        ('🔄 Auditoria', {
            'fields': ('atualizado_em',),
            'classes': ('collapse',)
        }),
    )
    
    def codigo_ticket_formatado(self, obj):
        """Exibe o código do ticket em destaque."""
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
    
    def status_badge(self, obj):
        """Exibe badge colorido do status."""
        cores = {
            'aguardando': '#17a2b8',
            'atendendo': '#ffc107',
            'finalizado': '#28a745',
            'cancelado': '#dc3545'
        }
        cor = cores.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: bold; text-transform: uppercase;">{}</span>',
            cor, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def posicao_fila_badge(self, obj):
        """Exibe a posição na fila com badge."""
        posicao = obj.posicao_fila
        if posicao:
            if posicao <= 3:
                cor = '#dc3545'  # Vermelho para primeiros
            elif posicao <= 10:
                cor = '#ffc107'  # Amarelo para top 10
            else:
                cor = '#6c757d'  # Cinza para demais
            return format_html(
                '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 50%; font-weight: bold; font-size: 12px;">{}</span>',
                cor, posicao
            )
        return format_html('<span style="color: #6c757d;">-</span>')
    posicao_fila_badge.short_description = 'Posição'
    
    def posicao_fila_detalhada(self, obj):
        """Exibe a posição na fila com detalhes."""
        posicao = obj.posicao_fila
        if posicao:
            total = Ticket.objects.filter(demanda=obj.demanda, status__in=['aguardando', 'atendendo']).count()
            return format_html(
                '<strong style="font-size: 24px; color: #007bff;">{}</strong> de <strong>{}</strong> na fila',
                posicao, total
            )
        return '-'
    posicao_fila_detalhada.short_description = 'Posição na Fila'
    
    def tempo_espera(self, obj):
        """Exibe o tempo de espera."""
        from django.utils import timezone
        if obj.status == 'aguardando':
            delta = timezone.now() - obj.criado_em
            horas = int(delta.total_seconds() // 3600)
            minutos = int((delta.total_seconds() % 3600) // 60)
            if horas > 0:
                return format_html('<span style="color: #dc3545; font-weight: bold;">{}h {}min</span>', horas, minutos)
            return format_html('<span style="color: #28a745;">{} min</span>', minutos)
        return '-'
    tempo_espera.short_description = 'Tempo de Espera'
    
    def tempo_total(self, obj):
        """Exibe o tempo total do ticket."""
        from django.utils import timezone
        if obj.finalizado_em:
            delta = obj.finalizado_em - obj.criado_em
        else:
            delta = timezone.now() - obj.criado_em
        horas = int(delta.total_seconds() // 3600)
        minutos = int((delta.total_seconds() % 3600) // 60)
        return f"{horas}h {minutos}min"
    tempo_total.short_description = 'Tempo Total'
    
    # Actions personalizadas
    def marcar_como_atendendo(self, request, queryset):
        """Marca tickets selecionados como 'atendendo'."""
        updated = queryset.update(status='atendendo')
        self.message_user(request, f'{updated} ticket(s) marcado(s) como "Atendendo".')
    marcar_como_atendendo.short_description = '✓ Marcar como Atendendo'
    
    def marcar_como_finalizado(self, request, queryset):
        """Marca tickets selecionados como 'finalizado'."""
        from django.utils import timezone
        for ticket in queryset:
            ticket.status = 'finalizado'
            if not ticket.finalizado_em:
                ticket.finalizado_em = timezone.now()
            ticket.save()
        self.message_user(request, f'{queryset.count()} ticket(s) marcado(s) como "Finalizado".')
    marcar_como_finalizado.short_description = '✓ Marcar como Finalizado'
    
    def marcar_como_cancelado(self, request, queryset):
        """Marca tickets selecionados como 'cancelado'."""
        updated = queryset.update(status='cancelado')
        self.message_user(request, f'{updated} ticket(s) marcado(s) como "Cancelado".')
    marcar_como_cancelado.short_description = '✗ Marcar como Cancelado'
