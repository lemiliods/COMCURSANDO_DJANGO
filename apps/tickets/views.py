from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from .models import Ticket
from .serializers import TicketSerializer, TicketCreateSerializer


class TicketViewSet(viewsets.ModelViewSet):
    """
    ViewSet para CRUD completo de Tickets.
    
    GET /api/tickets/ - Lista todos os tickets
    POST /api/tickets/ - Cria novo ticket
    GET /api/tickets/{id}/ - Detalhes de um ticket
    PUT /api/tickets/{id}/ - Atualiza ticket
    PATCH /api/tickets/{id}/ - Atualização parcial
    DELETE /api/tickets/{id}/ - Remove ticket
    POST /api/tickets/{id}/finalizar/ - Finaliza ticket
    """
    queryset = Ticket.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ['demanda', 'status']
    search_fields = ['codigo_ticket', 'cliente_nome']
    ordering_fields = ['criado_em', 'status']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TicketCreateSerializer
        return TicketSerializer
    
    @action(detail=True, methods=['post'])
    def finalizar(self, request, pk=None):
        """
        Action customizada para finalizar um ticket.
        
        POST /api/tickets/{id}/finalizar/
        """
        ticket = self.get_object()
        
        if ticket.status == 'finalizado':
            return Response(
                {'error': 'Ticket já está finalizado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ticket.status = 'finalizado'
        ticket.finalizado_em = timezone.now()
        ticket.save()
        
        serializer = self.get_serializer(ticket)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def fila_demanda(self, request):
        """
        Retorna todos os tickets aguardando de uma demanda específica.
        
        GET /api/tickets/fila_demanda/?demanda_id=1
        """
        demanda_id = request.query_params.get('demanda_id')
        
        if not demanda_id:
            return Response(
                {'error': 'demanda_id é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tickets = Ticket.objects.filter(
            demanda_id=demanda_id,
            status='aguardando'
        ).order_by('criado_em')
        
        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)
