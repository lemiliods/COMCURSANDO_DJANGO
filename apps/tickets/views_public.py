from django.shortcuts import render, redirect, get_object_or_404
from apps.concursos.models import Demanda
from apps.tickets.models import Ticket


def ticket_novo_view(request, demanda_id):
    """
    View para enviar prova de concurso.
    Cliente faz upload da prova (PDF ou imagem) e informa chave PIX.
    """
    demanda = get_object_or_404(Demanda, id=demanda_id)
    
    # Verificar se concurso está aberto e não tem prova aprovada
    if demanda.status != 'aberto':
        return render(request, 'public/ticket_form.html', {
            'demanda': demanda,
            'error': 'Este concurso não está mais aceitando envios.'
        })
    
    if demanda.tem_prova_aprovada:
        return render(request, 'public/ticket_form.html', {
            'demanda': demanda,
            'error': 'Este concurso já possui uma prova aprovada.'
        })
    
    if request.method == 'POST':
        cliente_nome = request.POST.get('cliente_nome', '').strip()
        cliente_pix = request.POST.get('cliente_pix', '').strip()
        arquivo_prova = request.FILES.get('arquivo_prova')
        
        # Validações
        errors = []
        if not cliente_nome:
            errors.append('Por favor, informe seu nome completo.')
        if not cliente_pix:
            errors.append('Por favor, informe sua chave PIX.')
        if not arquivo_prova:
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
                'errors': errors
            })
        
        # Criar ticket (envio de prova)
        ticket = Ticket.objects.create(
            demanda=demanda,
            cliente_nome=cliente_nome,
            cliente_pix=cliente_pix,
            arquivo_prova=arquivo_prova,
            status='aguardando'
        )
        
        # Atualizar status da demanda para em_analise
        demanda.status = 'em_analise'
        demanda.save()
        
        return redirect('ticket_success', ticket_id=ticket.id)
    
    return render(request, 'public/ticket_form.html', {
        'demanda': demanda
    })


def ticket_success_view(request, ticket_id):
    """
    View de sucesso após enviar prova.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    return render(request, 'public/ticket_success.html', {
        'ticket': ticket
    })
