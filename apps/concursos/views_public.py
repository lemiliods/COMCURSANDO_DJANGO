from django.shortcuts import render
from django.db.models import Q, Count
from apps.concursos.models import Demanda
from apps.tickets.models import Ticket


def home_view(request):
    """
    View pública para listagem de concursos.
    """
    # Filtros
    search = request.GET.get('search', '')
    banca = request.GET.get('banca', '')
    cargo = request.GET.get('cargo', '')
    
    # Query base - apenas concursos abertos
    demandas = Demanda.objects.filter(status='aberto')
    
    # Aplicar filtros
    if search:
        demandas = demandas.filter(
            Q(concurso__icontains=search) |
            Q(numero_edital__icontains=search) |
            Q(autarquia__icontains=search)
        )
    
    if banca:
        demandas = demandas.filter(banca=banca)
    
    if cargo:
        demandas = demandas.filter(cargo__icontains=cargo)
    
    # Anotar com total de tickets
    demandas = demandas.annotate(
        total_tickets=Count('tickets')
    ).order_by('-criado_em')
    
    # Lista de bancas para o filtro
    bancas = Demanda.objects.filter(status='aberto').values_list('banca', flat=True).distinct()
    
    # Estatísticas
    total_concursos = Demanda.objects.filter(status='aberto').count()
    total_tickets = Ticket.objects.count()
    tickets_aguardando = Ticket.objects.filter(status='aguardando').count()
    
    context = {
        'demandas': demandas,
        'bancas': sorted(bancas),
        'total_concursos': total_concursos,
        'total_tickets': total_tickets,
        'tickets_aguardando': tickets_aguardando,
    }
    
    return render(request, 'public/home.html', context)
