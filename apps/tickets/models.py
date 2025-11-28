from django.db import models
from apps.concursos.models import Demanda
from datetime import datetime


class Ticket(models.Model):
    """
    Modelo para gerenciar envio de provas de concursos.
    Cada ticket representa uma submissão de prova por um cliente.
    """
    
    STATUS_CHOICES = [
        ('aguardando', 'Aguardando Análise'),
        ('em_analise', 'Em Análise'),
        ('aprovado', 'Aprovado - Aguardando Pagamento'),
        ('pago', 'Pago e Concluído'),
        ('recusado', 'Recusado'),
    ]
    
    demanda = models.ForeignKey(
        Demanda,
        on_delete=models.CASCADE,
        related_name='tickets',
        verbose_name='Concurso'
    )
    cliente_nome = models.CharField(max_length=255, verbose_name='Nome do Cliente')
    cliente_whatsapp = models.CharField(max_length=20, verbose_name='WhatsApp', help_text='Número com código do país +55 e DDD (ex: +5511966149003)')
    cliente_pix = models.CharField(max_length=255, verbose_name='Chave PIX', help_text='CPF, e-mail, telefone ou chave aleatória')
    arquivo_prova = models.FileField(upload_to='provas/%Y/%m/', verbose_name='Arquivo da Prova', help_text='PDF ou imagem da prova')
    codigo_ticket = models.CharField(
        max_length=12, 
        unique=True, 
        verbose_name='Código do Envio'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='aguardando',
        verbose_name='Status'
    )
    observacoes_admin = models.TextField(blank=True, null=True, verbose_name='Observações do Admin', help_text='Motivo da recusa ou observações')
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Valor Pago')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Enviado em')
    analisado_em = models.DateTimeField(null=True, blank=True, verbose_name='Analisado em')
    pago_em = models.DateTimeField(null=True, blank=True, verbose_name='Pago em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        db_table = 'tickets'
        verbose_name = 'Envio de Prova'
        verbose_name_plural = 'Envios de Provas'
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['demanda', 'status']),
            models.Index(fields=['codigo_ticket']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.codigo_ticket} - {self.cliente_nome} ({self.demanda.concurso})"
    
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
