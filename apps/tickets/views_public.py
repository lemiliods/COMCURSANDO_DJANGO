from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from apps.concursos.models import Demanda
from apps.tickets.models import Ticket
from apps.tickets.notifications import enviar_email_fila, gerar_link_whatsapp_fila
import urllib.parse
import logging
import pytz

logger = logging.getLogger(__name__)


def enviar_mensagem_whatsapp(numero, ticket):
    """
    Gera link do WhatsApp para enviar mensagem automática.
    Retorna URL que pode ser usada para redirecionar ou abrir em nova aba.
    """
    mensagem = f"""🎯 *COMCURSANDO*

Olá! Recebemos sua prova do concurso *{ticket.demanda.concurso}*.

📋 *Código do envio:* {ticket.codigo_ticket}
✅ *Status:* Aguardando análise

Estamos analisando sua prova. Caso seja aprovada, entraremos em contato e enviaremos o pagamento via PIX.

Qualquer dúvida, responda esta mensagem!

Obrigado! 🚀"""
    
    # Número da empresa
    numero_empresa = "5511966149003"
    mensagem_encoded = urllib.parse.quote(mensagem)
    
    # Link do WhatsApp Web (não envia automaticamente, só abre conversa)
    whatsapp_url = f"https://wa.me/{numero}?text={mensagem_encoded}"
    
    return whatsapp_url


def ticket_novo_view(request, demanda_id):
    """
    View para enviar prova de concurso ou entrar na fila.
    - 1ª pessoa: Envia prova diretamente
    - Demais: Entram na fila de espera
    """
    demanda = get_object_or_404(Demanda, id=demanda_id)
    
    # Verificar se concurso aceita envios (aberto ou em_analise)
    if demanda.status not in ['aberto', 'em_analise']:
        return render(request, 'public/ticket_form.html', {
            'demanda': demanda,
            'error': 'Este concurso não está mais aceitando envios.'
        })
    
    if demanda.tem_prova_aprovada:
        return render(request, 'public/ticket_form.html', {
            'demanda': demanda,
            'error': 'Este concurso já possui uma prova aprovada.'
        })
    
    # Verificar se existe alguém já enviando prova (em análise ou aguardando)
    tem_prova_em_analise = Ticket.objects.filter(
        demanda=demanda,
        status__in=['aguardando', 'em_analise']
    ).exists()
    
    # Verificar total na fila
    total_na_fila = Ticket.objects.filter(
        demanda=demanda,
        status__in=['na_fila', 'notificado', 'aguardando', 'em_analise']
    ).count()
    
    if request.method == 'POST':
        cliente_nome = request.POST.get('cliente_nome', '').strip()
        cliente_email = request.POST.get('cliente_email', '').strip()
        cliente_whatsapp = request.POST.get('cliente_whatsapp', '').strip()
        cliente_pix = request.POST.get('cliente_pix', '').strip()
        arquivo_prova = request.FILES.get('arquivo_prova')
        
        # Se não tem prova em análise, permite envio direto
        pode_enviar_agora = not tem_prova_em_analise
        
        # Normalizar WhatsApp: adicionar +55 se não tiver código do país
        if cliente_whatsapp and not cliente_whatsapp.startswith('+'):
            # Remove caracteres especiais
            whatsapp_limpo = cliente_whatsapp.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            # Se não começar com 55, adiciona +55
            if not whatsapp_limpo.startswith('55'):
                cliente_whatsapp = f'+55{whatsapp_limpo}'
            else:
                cliente_whatsapp = f'+{whatsapp_limpo}'
        
        # Validações
        errors = []
        if not cliente_nome:
            errors.append('Por favor, informe seu nome completo.')
        if not cliente_whatsapp:
            errors.append('Por favor, informe seu WhatsApp.')
        else:
            # Validar formato do WhatsApp
            whatsapp_numeros = cliente_whatsapp.replace('+', '')
            if not whatsapp_numeros.isdigit():
                errors.append('WhatsApp deve conter apenas números (código do país + DDD + número).')
            elif len(whatsapp_numeros) < 12 or len(whatsapp_numeros) > 13:
                errors.append('WhatsApp inválido. Formato esperado: +5511966149003 (código país + DDD + número)')
            
            # VERIFICAR SE JÁ EXISTE ENVIO DESTE WHATSAPP PARA ESTA DEMANDA
            envio_existente = Ticket.objects.filter(
                demanda=demanda,
                cliente_whatsapp=cliente_whatsapp,
                status__in=['na_fila', 'notificado', 'aguardando', 'em_analise', 'aprovado']
            ).first()
            
            if envio_existente:
                # Calcular posição na fila
                posicao = Ticket.objects.filter(
                    demanda=demanda,
                    status__in=['na_fila', 'notificado', 'aguardando', 'em_analise'],
                    criado_em__lt=envio_existente.criado_em
                ).count() + 1
                
                errors.append(f'Você já enviou uma prova para este concurso! Código: {envio_existente.codigo_ticket}. Posição na fila: {posicao}º')
        
        if not cliente_pix:
            errors.append('Por favor, informe sua chave PIX.')
        
        # Validar arquivo apenas se for enviar agora
        if pode_enviar_agora and not arquivo_prova:
            errors.append('Por favor, envie o arquivo da prova.')
        
        # Validar tipo de arquivo
        if arquivo_prova:
            allowed_types = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png']
            if arquivo_prova.content_type not in allowed_types:
                errors.append('Tipo de arquivo inválido. Envie PDF, JPG ou PNG.')
            
            # Validar tamanho (10MB)
            if arquivo_prova.size > 10 * 1024 * 1024:
                errors.append('Arquivo muito grande. Tamanho máximo: 10MB.')
        
        if errors:
            return render(request, 'public/ticket_form.html', {
                'demanda': demanda,
                'errors': errors,
                'pode_enviar_agora': pode_enviar_agora,
                'tem_prova_em_analise': tem_prova_em_analise
            })
        
        # Criar ticket
        if pode_enviar_agora:
            # 1ª pessoa: Envia prova diretamente e vai para análise
            ticket = Ticket.objects.create(
                demanda=demanda,
                cliente_nome=cliente_nome,
                cliente_email=cliente_email,
                cliente_whatsapp=cliente_whatsapp,
                cliente_pix=cliente_pix,
                arquivo_prova=arquivo_prova,
                status='em_analise'  # Já vai direto para análise
            )
            
            # Atualizar demanda para em_analise
            demanda.status = 'em_analise'
            demanda.save()
            
            # Enviar mensagem WhatsApp confirmação
            enviar_mensagem_whatsapp(cliente_whatsapp, ticket)
        else:
            # Demais pessoas: Entram na fila de espera
            ticket = Ticket.objects.create(
                demanda=demanda,
                cliente_nome=cliente_nome,
                cliente_email=cliente_email,
                cliente_whatsapp=cliente_whatsapp,
                cliente_pix=cliente_pix,
                status='na_fila'  # Entra na fila
            )
            
            # Enviar notificações de entrada na fila
            try:
                enviar_email_fila(ticket)
                whatsapp_link = gerar_link_whatsapp_fila(ticket)
                logger.info(f"Cliente entrou na fila - Ticket: {ticket.codigo_ticket}, WhatsApp: {whatsapp_link}")
            except Exception as e:
                logger.error(f"Erro ao enviar notificações de fila: {str(e)}")
        
        return redirect('ticket_success', ticket_id=ticket.id)
    
    # GET request - renderizar formulário
    return render(request, 'public/ticket_form.html', {
        'demanda': demanda,
        'pode_enviar_agora': not tem_prova_em_analise,
        'tem_prova_em_analise': tem_prova_em_analise,
        'total_na_fila': total_na_fila
    })


def ticket_success_view(request, ticket_id):
    """
    View de sucesso após enviar prova.
    Mostra a posição do ticket na fila.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    # Calcular posição na fila (incluindo todos os status ativos)
    posicao_fila = Ticket.objects.filter(
        demanda=ticket.demanda,
        status__in=['na_fila', 'notificado', 'aguardando', 'em_analise'],
        criado_em__lt=ticket.criado_em
    ).count() + 1
    
    total_fila = Ticket.objects.filter(
        demanda=ticket.demanda,
        status__in=['na_fila', 'notificado', 'aguardando', 'em_analise']
    ).count()
    
    return render(request, 'public/ticket_success.html', {
        'ticket': ticket,
        'posicao_fila': posicao_fila,
        'total_fila': total_fila
    })


def ticket_upload_view(request, ticket_id):
    """
    View para upload de prova quando o participante é notificado.
    Apenas para tickets com status 'notificado'.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    # Verificar se o ticket está notificado
    if ticket.status != 'notificado':
        return render(request, 'public/ticket_upload.html', {
            'ticket': ticket,
            'error': 'Este link não é mais válido. O status do seu ticket mudou.'
        })
    
    # Verificar se o prazo expirou
    if ticket.prazo_envio and timezone.now() > ticket.prazo_envio:
        ticket.status = 'expirado'
        ticket.save()
        
        # Notificar próximo da fila
        from apps.tickets.notifications import notificar_proximo_da_fila
        try:
            notificar_proximo_da_fila(ticket.demanda)
        except Exception as e:
            logger.error(f"Erro ao notificar próximo após expiração: {str(e)}")
        
        return render(request, 'public/ticket_upload.html', {
            'ticket': ticket,
            'error': 'Seu prazo de 1 hora expirou. O próximo da fila foi notificado.'
        })
    
    if request.method == 'POST':
        arquivo_prova = request.FILES.get('arquivo_prova')
        
        errors = []
        
        # Validar arquivo
        if not arquivo_prova:
            errors.append('Por favor, envie o arquivo da prova.')
        else:
            # Validar tipo
            allowed_types = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png']
            if arquivo_prova.content_type not in allowed_types:
                errors.append('Tipo de arquivo inválido. Envie PDF, JPG ou PNG.')
            
            # Validar tamanho (10MB)
            if arquivo_prova.size > 10 * 1024 * 1024:
                errors.append('Arquivo muito grande. Tamanho máximo: 10MB.')
        
        if errors:
            return render(request, 'public/ticket_upload.html', {
                'ticket': ticket,
                'errors': errors
            })
        
        # Atualizar ticket
        ticket.arquivo_prova = arquivo_prova
        ticket.status = 'em_analise'
        ticket.save()
        
        # Atualizar demanda
        ticket.demanda.status = 'em_analise'
        ticket.demanda.save()
        
        logger.info(f"Ticket {ticket.codigo_ticket} - Upload realizado após notificação")
        
        return redirect('ticket_success', ticket_id=ticket.id)
    
    # GET - mostrar formulário de upload
    # Converter prazo para horário de Brasília
    prazo_brasilia = ticket.prazo_envio.astimezone(pytz.timezone('America/Sao_Paulo'))
    prazo_formatado = prazo_brasilia.strftime('%d/%m/%Y %H:%M')
    
    return render(request, 'public/ticket_upload.html', {
        'ticket': ticket,
        'prazo_formatado': prazo_formatado
    })
