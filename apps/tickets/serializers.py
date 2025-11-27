from rest_framework import serializers
from .models import Ticket
from apps.concursos.serializers import DemandaSerializer


class TicketSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Ticket.
    """
    demanda_detalhes = DemandaSerializer(source='demanda', read_only=True)
    posicao_fila = serializers.ReadOnlyField()
    
    class Meta:
        model = Ticket
        fields = ['id', 'demanda', 'demanda_detalhes', 'cliente_nome', 
                  'codigo_ticket', 'status', 'posicao_fila', 
                  'criado_em', 'finalizado_em']
        read_only_fields = ['id', 'codigo_ticket', 'criado_em', 'finalizado_em']


class TicketCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de Ticket (sem código, gerado automaticamente).
    """
    
    class Meta:
        model = Ticket
        fields = ['demanda', 'cliente_nome']
