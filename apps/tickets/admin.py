from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from django.utils import timezone
from .models import Ticket
from .notifications import notificar_proximo_da_fila
import urllib.parse
import logging

logger = logging.getLogger(__name__)


def enviar_notificacao_encerramento(ticket):
    """
    Gera link do WhatsApp para notificar participante sobre encerramento da demanda.
    Retorna URL que pode ser aberta para enviar mensagem via WhatsApp Web.
    """
    mensagem = f"""🎯 *COMCURSANDO - Atualização*

Olá, {ticket.cliente_nome.split()[0]}!

Informamos que a demanda do concurso *{ticket.demanda.concurso}* (Edital: {ticket.demanda.numero_edital}) foi encerrada.

📋 *Seu código de envio:* {ticket.codigo_ticket}

✅ Outra prova foi aprovada e selecionada para esta demanda.

Agradecemos muito pela sua disposição em colaborar! 
Em uma próxima oportunidade será a sua vez. 🚀

Obrigado pela compreensão!

---
Continue acompanhando nossos concursos disponíveis em:
https://comcursando.com.br"""
    
    mensagem_encoded = urllib.parse.quote(mensagem)
    numero_limpo = ticket.cliente_whatsapp.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    whatsapp_url = f"https://wa.me/{numero_limpo}?text={mensagem_encoded}"
    
    return whatsapp_url


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """
    Configuração do admin para Envios de Prova.
    """
    list_display = ['codigo_ticket_formatado', 'cliente_nome', 'whatsapp_link', 'concurso_info', 'pix_info', 'status_badge', 'arquivo_preview', 'valor_info', 'criado_em']
    list_filter = ['status', 'demanda__banca', 'criado_em', 'analisado_em', 'pago_em']
    search_fields = ['codigo_ticket', 'cliente_nome', 'cliente_whatsapp', 'cliente_pix', 'demanda__concurso', 'demanda__numero_edital']
    ordering = ['-criado_em']
    date_hierarchy = 'criado_em'
    readonly_fields = ['codigo_ticket', 'criado_em', 'atualizado_em', 'analisado_em', 'pago_em']
    list_per_page = 25
    actions = ['aprovar_prova', 'recusar_prova', 'marcar_como_pago', 'excluir_tickets']
    
    fieldsets = (
        ('📄 Informações do Envio', {
            'fields': ('codigo_ticket', 'demanda', 'cliente_nome', 'cliente_whatsapp', 'cliente_pix'),
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
    
    def whatsapp_link(self, obj):
        """Exibe link clicável para WhatsApp."""
        if obj.cliente_whatsapp:
            # Remove + do número para o link wa.me
            numero_limpo = obj.cliente_whatsapp.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            return format_html(
                '<a href="https://wa.me/{}" target="_blank" style="background: #25D366; color: white; padding: 4px 10px; border-radius: 4px; text-decoration: none; font-size: 11px;"><i class="fab fa-whatsapp"></i> {}</a>',
                numero_limpo,
                obj.cliente_whatsapp
            )
        return format_html('<span style="color: #6c757d;">-</span>')
    whatsapp_link.short_description = 'WhatsApp'
    
    def pix_info(self, obj):
        """Exibe a chave PIX."""
        if obj.cliente_pix:
            return format_html(
                '<span style="font-family: monospace; font-size: 12px; background: #e8f5e9; color: #2e7d32; padding: 4px 8px; border-radius: 3px;">{}</span>',
                obj.cliente_pix
            )
        return format_html('<span style="color: #6c757d;">-</span>')
    pix_info.short_description = 'Chave PIX'
    
    def arquivo_preview(self, obj):
        """Exibe preview/link do arquivo."""
        if obj.arquivo_prova and hasattr(obj.arquivo_prova, 'url'):
            return format_html(
                '<a href="{}" target="_blank" style="background: #007bff; color: white; padding: 4px 12px; border-radius: 4px; text-decoration: none; font-size: 11px;">📄 Ver Prova</a>',
                obj.arquivo_prova.url
            )
        return format_html('<span style="color: #dc3545;">Sem arquivo</span>')
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
        """Recusa provas selecionadas e notifica próximo da fila."""
        count = 0
        notificados = []
        
        for ticket in queryset:
            if ticket.status in ['aguardando', 'em_analise']:
                ticket.status = 'recusado'
                ticket.analisado_em = timezone.now()
                # Retornar demanda para aberto
                ticket.demanda.status = 'aberto'
                ticket.demanda.save()
                ticket.save()
                count += 1
                
                # Notificar próximo da fila
                try:
                    proximo = notificar_proximo_da_fila(ticket.demanda)
                    if proximo:
                        notificados.append({
                            'nome': proximo.cliente_nome,
                            'codigo': proximo.codigo_ticket,
                            'whatsapp': proximo.cliente_whatsapp
                        })
                        logger.info(f"Próximo da fila notificado: {proximo.codigo_ticket}")
                except Exception as e:
                    logger.error(f"Erro ao notificar próximo da fila: {str(e)}")
        
        # Mensagem com informações de notificação
        msg = f'{count} prova(s) recusada(s). Demanda(s) voltaram para "aberto". '
        if notificados:
            msg += f'{len(notificados)} pessoa(s) na fila notificada(s) automaticamente: '
            msg += ', '.join([f"{n['nome']} ({n['codigo']})" for n in notificados])
        
        self.message_user(request, msg)
    recusar_prova.short_description = '✗ Recusar Prova e Notificar Próximo'
    
    def marcar_como_pago(self, request, queryset):
        """
        Marca provas aprovadas como pagas e notifica outros participantes.
        Envia mensagem via WhatsApp para todos os outros que tiveram provas recusadas/aguardando.
        """
        count = 0
        notificacoes = []
        
        for ticket in queryset:
            if ticket.status == 'aprovado':
                # Buscar outros tickets da mesma demanda que NÃO foram aprovados
                outros_tickets = Ticket.objects.filter(
                    demanda=ticket.demanda,
                    status__in=['aguardando', 'em_analise', 'recusado']
                ).exclude(id=ticket.id)
                
                # Marcar ticket como pago
                ticket.status = 'pago'
                ticket.pago_em = timezone.now()
                if not ticket.valor_pago:
                    ticket.valor_pago = ticket.demanda.valor_recompensa
                
                # Marcar demanda como concluída
                ticket.demanda.status = 'concluido'
                ticket.demanda.save()
                ticket.save()
                
                # Recusar automaticamente os outros tickets e gerar links de notificação
                for outro_ticket in outros_tickets:
                    if outro_ticket.status != 'recusado':
                        outro_ticket.status = 'recusado'
                        outro_ticket.analisado_em = timezone.now()
                        outro_ticket.observacoes_admin = 'Demanda encerrada - outra prova foi selecionada'
                        outro_ticket.save()
                    
                    # Gerar link de notificação
                    if outro_ticket.cliente_whatsapp:
                        whatsapp_link = enviar_notificacao_encerramento(outro_ticket)
                        notificacoes.append({
                            'nome': outro_ticket.cliente_nome,
                            'codigo': outro_ticket.codigo_ticket,
                            'link': whatsapp_link
                        })
                
                count += 1
        
        # Mensagem de sucesso com links de WhatsApp
        if notificacoes:
            msg = f'{count} prova(s) marcada(s) como PAGA. '
            msg += f'{len(notificacoes)} participante(s) precisam ser notificados. '
            msg += 'Clique nos links abaixo para enviar as mensagens via WhatsApp:<br><br>'
            for notif in notificacoes:
                msg += f'<a href="{notif["link"]}" target="_blank" style="display:inline-block; background:#25D366; color:white; padding:8px 15px; margin:5px; border-radius:5px; text-decoration:none;">📱 {notif["nome"]} ({notif["codigo"]})</a><br>'
            
            from django.contrib import messages
            from django.utils.safestring import mark_safe
            messages.success(request, mark_safe(msg))
        else:
            self.message_user(request, f'{count} prova(s) marcada(s) como PAGA.')
    
    marcar_como_pago.short_description = '💰 Marcar como Pago e Notificar'
    
    def excluir_tickets(self, request, queryset):
        """
        Exclui tickets selecionados (útil para remover testes ou entradas inválidas).
        """
        count = queryset.count()
        tickets_info = []
        
        for ticket in queryset:
            tickets_info.append({
                'codigo': ticket.codigo_ticket,
                'nome': ticket.cliente_nome,
                'status': ticket.get_status_display()
            })
        
        # Excluir os tickets
        queryset.delete()
        
        # Mensagem detalhada
        msg = f'{count} ticket(s) excluído(s) com sucesso:<br>'
        for info in tickets_info:
            msg += f'• {info["codigo"]} - {info["nome"]} ({info["status"]})<br>'
        
        from django.contrib import messages
        from django.utils.safestring import mark_safe
        messages.success(request, mark_safe(msg))
    
    excluir_tickets.short_description = '🗑️ Excluir Tickets Selecionados'
