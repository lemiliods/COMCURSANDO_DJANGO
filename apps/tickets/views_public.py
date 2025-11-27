from django.shortcuts import render, redirect, get_object_or_404
from apps.concursos.models import Demanda
from apps.tickets.models import Ticket


def ticket_novo_view(request, demanda_id):
    """
    View para criar novo ticket.
    """
    demanda = get_object_or_404(Demanda, id=demanda_id)
    
    # Verificar se concurso está aberto
    if demanda.status != 'aberto':
        return render(request, 'public/ticket_form.html', {
            'demanda': demanda,
            'error': 'Este concurso não está mais aceitando tickets.'
        })
    
    if request.method == 'POST':
        cliente_nome = request.POST.get('cliente_nome', '').strip()
        
        if not cliente_nome:
            return render(request, 'public/ticket_form.html', {
                'demanda': demanda,
                'error': 'Por favor, informe seu nome completo.'
            })
        
        # Criar ticket
        ticket = Ticket.objects.create(
            demanda=demanda,
            cliente_nome=cliente_nome,
            status='aguardando'
        )
        
        return redirect('ticket_success', ticket_id=ticket.id)
    
    return render(request, 'public/ticket_form.html', {
        'demanda': demanda
    })


def ticket_success_view(request, ticket_id):
    """
    View de sucesso após gerar ticket.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)
    posicao = ticket.posicao_fila
    
    return render(request, 'public/ticket_success.html', {
        'ticket': ticket,
        'posicao': posicao
    })
