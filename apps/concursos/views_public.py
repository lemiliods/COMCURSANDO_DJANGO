from django.shortcuts import render
from django.db.models import Q, Count
from apps.concursos.models import Demanda
from apps.tickets.models import Ticket


def home_view(request):
    """
    View pública para listagem de concursos disponíveis para envio de provas.
    Mostra concursos abertos ou em análise que ainda não têm prova aprovada.
    """
    # Filtros
    search = request.GET.get('search', '')
    banca = request.GET.get('banca', '')
    cargo = request.GET.get('cargo', '')
    
    # Query base - concursos abertos OU em análise (aguardando mais provas)
    demandas = Demanda.objects.filter(status__in=['aberto', 'em_analise'])
    
    # Filtrar concursos que NÃO têm prova aprovada ou paga
    demandas_list = []
    for d in demandas:
        if not d.tem_prova_aprovada:
            # Adicionar informações de fila
            d.total_na_fila = d.tickets.filter(status__in=['aguardando', 'em_analise']).count()
            demandas_list.append(d)
    
    demandas = demandas_list
    
    # Aplicar filtros de busca
    if search:
        demandas = [d for d in demandas if (
            search.lower() in d.concurso.lower() or
            search.lower() in d.numero_edital.lower() or
            search.lower() in d.autarquia.lower()
        )]
    
    if banca:
        demandas = [d for d in demandas if d.banca == banca]
    
    if cargo:
        demandas = [d for d in demandas if cargo.lower() in d.cargo.lower()]
    
    # Lista de bancas para o filtro
    bancas = Demanda.objects.filter(status__in=['aberto', 'em_analise']).values_list('banca', flat=True).distinct()
    
    # Estatísticas
    total_concursos = len(demandas)
    total_envios = Ticket.objects.count()
    envios_em_analise = Ticket.objects.filter(status='em_analise').count()
    
    context = {
        'demandas': demandas,
        'bancas': sorted(bancas),
        'total_concursos': total_concursos,
        'total_envios': total_envios,
        'envios_em_analise': envios_em_analise,
    }
    
    return render(request, 'public/home.html', context)
