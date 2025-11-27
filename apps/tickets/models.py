from django.db import models
from apps.concursos.models import Demanda
from datetime import datetime


class Ticket(models.Model):
    """
    Modelo para gerenciar tickets de atendimento vinculados a demandas.
    Cada ticket representa um cliente na fila para uma demanda específica.
    """
    
    STATUS_CHOICES = [
        ('aguardando', 'Aguardando'),
        ('em_atendimento', 'Em Atendimento'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    ]
    
    demanda = models.ForeignKey(
        Demanda,
        on_delete=models.CASCADE,
        related_name='tickets',
        verbose_name='Demanda'
    )
    cliente_nome = models.CharField(max_length=255, verbose_name='Nome do Cliente')
    codigo_ticket = models.CharField(
        max_length=12, 
        unique=True, 
        verbose_name='Código do Ticket'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='aguardando',
        verbose_name='Status'
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    finalizado_em = models.DateTimeField(null=True, blank=True, verbose_name='Finalizado em')
    
    class Meta:
        db_table = 'tickets'
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ['criado_em']
        indexes = [
            models.Index(fields=['demanda', 'status']),
            models.Index(fields=['codigo_ticket']),
        ]
    
    def __str__(self):
        return f"{self.codigo_ticket} - {self.cliente_nome}"
    
    def save(self, *args, **kwargs):
        """
        Gera código do ticket no formato DDMMYYnnnn se não existir.
        DDMMYY = data atual
        nnnn = sequencial do dia (0001, 0002, etc.)
        """
        if not self.codigo_ticket:
            hoje = datetime.now()
            prefixo = hoje.strftime('%d%m%y')
            
            # Busca o último ticket do dia para calcular sequencial
            ultimo_ticket = Ticket.objects.filter(
                codigo_ticket__startswith=prefixo
            ).order_by('-codigo_ticket').first()
            
            if ultimo_ticket:
                # Extrai os últimos 4 dígitos e incrementa
                ultimo_seq = int(ultimo_ticket.codigo_ticket[-4:])
                novo_seq = ultimo_seq + 1
            else:
                novo_seq = 1
            
            self.codigo_ticket = f"{prefixo}{novo_seq:04d}"
        
        super().save(*args, **kwargs)
    
    @property
    def posicao_fila(self):
        """
        Calcula a posição do ticket na fila da demanda.
        Considera apenas tickets aguardando, ordenados por data de criação.
        """
        if self.status != 'aguardando':
            return None
        
        tickets_aguardando = Ticket.objects.filter(
            demanda=self.demanda,
            status='aguardando',
            criado_em__lte=self.criado_em
        ).order_by('criado_em')
        
        posicao = 1
        for ticket in tickets_aguardando:
            if ticket.id == self.id:
                return posicao
            posicao += 1
        
        return None
