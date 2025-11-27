from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Demanda
from .serializers import DemandaSerializer


class DemandaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para CRUD completo de Demandas.
    
    GET /api/demandas/ - Lista todas as demandas
    POST /api/demandas/ - Cria nova demanda
    GET /api/demandas/{id}/ - Detalhes de uma demanda
    PUT /api/demandas/{id}/ - Atualiza demanda
    PATCH /api/demandas/{id}/ - Atualização parcial
    DELETE /api/demandas/{id}/ - Remove demanda
    """
    queryset = Demanda.objects.all()
    serializer_class = DemandaSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'banca', 'cargo']
    search_fields = ['concurso', 'numero_edital', 'cargo', 'autarquia']
    ordering_fields = ['criado_em', 'data_concurso', 'concurso']
