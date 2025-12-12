"""
Sistema de notificações para tickets (Email e WhatsApp)
"""
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import urllib.parse
import logging
import pytz

logger = logging.getLogger(__name__)


def enviar_email_fila(ticket):
    """
    Envia email notificando que o cliente entrou na fila de espera.
    """
    if not ticket.cliente_email:
        return False
    
    assunto = f'🎯 Você entrou na fila - {ticket.demanda.concurso}'
    
    mensagem = f"""
Olá {ticket.cliente_nome}!

Você entrou na fila de espera para enviar sua prova do concurso:
📚 {ticket.demanda.concurso}
📋 Edital: {ticket.demanda.numero_edital}
💼 Cargo: {ticket.demanda.cargo}

🎫 Código do seu envio: {ticket.codigo_ticket}

Você será notificado por WhatsApp quando for sua vez de enviar a prova.
Terá 1 hora para fazer o upload após ser notificado.

💰 Recompensa: R$ {ticket.demanda.valor_recompensa}

Aguarde! Entraremos em contato em breve.

--
COMCURSANDO
https://comcursando.com.br
    """
    
    try:
        send_mail(
            assunto,
            mensagem,
            settings.DEFAULT_FROM_EMAIL,
            [ticket.cliente_email],
            fail_silently=False,
        )
        logger.info(f"Email enviado para {ticket.cliente_email} - Ticket {ticket.codigo_ticket}")
        return True
    except Exception as e:
        logger.error(f"Erro ao enviar email para {ticket.cliente_email}: {str(e)}")
        return False


def enviar_email_sua_vez(ticket, link_upload):
    """
    Envia email notificando que chegou a vez do cliente enviar a prova.
    """
    if not ticket.cliente_email:
        return False
    
    assunto = f'⏰ SUA VEZ! Envie sua prova agora - {ticket.demanda.concurso}'
    
    mensagem = f"""
Olá {ticket.cliente_nome}!

🎉 CHEGOU SUA VEZ de enviar a prova do concurso:
📚 {ticket.demanda.concurso}
📋 Edital: {ticket.demanda.numero_edital}

⚠️ ATENÇÃO: Você tem 1 HORA para enviar sua prova!

🔗 Clique no link abaixo para fazer o upload:
{link_upload}

⏱️ Prazo: {ticket.prazo_envio.astimezone(pytz.timezone('America/Sao_Paulo')).strftime('%d/%m/%Y às %H:%M')} (horário de Brasília)

💰 Recompensa: R$ {ticket.demanda.valor_recompensa}

Não perca essa oportunidade!

--
COMCURSANDO
https://comcursando.com.br
    """
    
    try:
        send_mail(
            assunto,
            mensagem,
            settings.DEFAULT_FROM_EMAIL,
            [ticket.cliente_email],
            fail_silently=False,
        )
        logger.info(f"Email 'sua vez' enviado para {ticket.cliente_email} - Ticket {ticket.codigo_ticket}")
        return True
    except Exception as e:
        logger.error(f"Erro ao enviar email 'sua vez' para {ticket.cliente_email}: {str(e)}")
        return False


def gerar_link_whatsapp_fila(ticket):
    """
    Gera link do WhatsApp para notificar entrada na fila.
    """
    mensagem = f"""🎯 *COMCURSANDO - Fila de Espera*

Olá *{ticket.cliente_nome}*!

Você entrou na fila de espera para enviar sua prova:
📚 *{ticket.demanda.concurso}*
📋 Edital: {ticket.demanda.numero_edital}

🎫 *Código:* {ticket.codigo_ticket}

Você será notificado quando for sua vez de enviar a prova.
Terá *1 hora* para fazer o upload.

💰 Recompensa: *R$ {ticket.demanda.valor_recompensa}*

Aguarde! 🚀"""
    
    numero = ticket.cliente_whatsapp.replace('+', '').replace(' ', '').replace('-', '')
    mensagem_encoded = urllib.parse.quote(mensagem)
    return f"https://wa.me/{numero}?text={mensagem_encoded}"


def gerar_link_whatsapp_sua_vez(ticket, link_upload):
    """
    Gera link do WhatsApp para notificar que chegou a vez de enviar.
    """
    # Converter para horário de Brasília
    prazo_brasilia = ticket.prazo_envio.astimezone(pytz.timezone('America/Sao_Paulo'))
    prazo_formatado = prazo_brasilia.strftime('%d/%m/%Y às %H:%M')
    
    mensagem = f"""🎉 *SUA VEZ! ENVIE SUA PROVA AGORA*

Olá *{ticket.cliente_nome}*!

⏰ *ATENÇÃO: Você tem 1 HORA para enviar!*

📚 Concurso: *{ticket.demanda.concurso}*
📋 Edital: {ticket.demanda.numero_edital}

🔗 *Link para upload:*
{link_upload}

⏱️ *Prazo:* {prazo_formatado} (horário de Brasília)
💰 *Recompensa:* R$ {ticket.demanda.valor_recompensa}

Não perca essa oportunidade! 🚀

--
COMCURSANDO
comcursando.com.br"""
    
    numero = ticket.cliente_whatsapp.replace('+', '').replace(' ', '').replace('-', '')
    mensagem_encoded = urllib.parse.quote(mensagem)
    return f"https://wa.me/{numero}?text={mensagem_encoded}"


def notificar_proximo_da_fila(demanda):
    """
    Notifica o próximo cliente na fila que é sua vez de enviar a prova.
    Retorna o ticket notificado ou None.
    """
    from apps.tickets.models import Ticket
    
    # Buscar próximo da fila
    proximo = Ticket.objects.filter(
        demanda=demanda,
        status='na_fila'
    ).order_by('criado_em').first()
    
    if not proximo:
        logger.info(f"Nenhum ticket na fila para demanda {demanda.id}")
        return None
    
    # Atualizar ticket
    proximo.status = 'notificado'
    proximo.notificado_em = timezone.now()
    proximo.prazo_envio = timezone.now() + timedelta(hours=1)
    proximo.save()
    
    # Gerar link de upload (será implementado)
    link_upload = f"https://comcursando.com.br/ticket/upload/{proximo.id}/"
    
    # Enviar notificações
    email_enviado = enviar_email_sua_vez(proximo, link_upload)
    whatsapp_link = gerar_link_whatsapp_sua_vez(proximo, link_upload)
    
    logger.info(f"Próximo da fila notificado: Ticket {proximo.codigo_ticket} - Email: {email_enviado}")
    logger.info(f"Link WhatsApp: {whatsapp_link}")
    
    return proximo


def enviar_email_recusa(ticket, motivo):
    """
    Envia email notificando que a prova foi recusada com o motivo.
    """
    if not ticket.cliente_email and not ticket.cliente_whatsapp:
        return False
    
    assunto = f'❌ Prova Recusada - {ticket.demanda.concurso}'
    
    mensagem = f"""
Olá {ticket.cliente_nome}!

Informamos que sua prova do concurso {ticket.demanda.concurso} foi analisada e infelizmente foi RECUSADA.

📋 *Código do envio:* {ticket.codigo_ticket}
📚 *Concurso:* {ticket.demanda.concurso}
📋 *Edital:* {ticket.demanda.numero_edital}

*Motivo da Recusa:*
{motivo}

A demanda foi reaberta e outras provas poderão ser enviadas.

Agradecemos sua participação!

--
COMCURSANDO
https://comcursando.com.br
    """
    
    try:
        if ticket.cliente_email:
            send_mail(
                assunto,
                mensagem,
                settings.DEFAULT_FROM_EMAIL,
                [ticket.cliente_email],
                fail_silently=False,
            )
            logger.info(f"Email de recusa enviado para {ticket.cliente_email} - Ticket {ticket.codigo_ticket}")
            return True
    except Exception as e:
        logger.error(f"Erro ao enviar email de recusa: {str(e)}")
        return False


def gerar_link_whatsapp_recusa(ticket, motivo):
    """
    Gera link do WhatsApp para notificar recusa da prova.
    """
    mensagem = f"""❌ *PROVA RECUSADA*

Olá *{ticket.cliente_nome}*!

Sua prova do concurso foi analisada e infelizmente foi recusada.

📋 *Código:* {ticket.codigo_ticket}
📚 *Concurso:* {ticket.demanda.concurso}

*Motivo da Recusa:*
{motivo}

A demanda foi reaberta e outras provas poderão ser enviadas.

Agradecemos sua participação!

--
COMCURSANDO
comcursando.com.br"""
    
    numero = ticket.cliente_whatsapp.replace('+', '').replace(' ', '').replace('-', '')
    mensagem_encoded = urllib.parse.quote(mensagem)
    return f"https://wa.me/{numero}?text={mensagem_encoded}"
