from django.db import models


class Demanda(models.Model):
    """
    Modelo para gerenciar demandas de concursos públicos.
    Cada demanda representa um concurso/edital que precisa de prova.
    """
    
    STATUS_CHOICES = [
        ('aberto', 'Aberto - Aguardando Prova'),
        ('em_analise', 'Em Análise'),
        ('concluido', 'Concluído - Prova Cadastrada'),
        ('cancelado', 'Cancelado'),
    ]
    
    concurso = models.CharField(max_length=255, verbose_name='Nome do Concurso')
    numero_edital = models.CharField(max_length=50, verbose_name='Número do Edital')
    banca = models.CharField(max_length=100, verbose_name='Banca Examinadora')
    data_concurso = models.DateField(verbose_name='Data do Concurso')
    cargo = models.CharField(max_length=255, verbose_name='Cargo')
    autarquia = models.CharField(max_length=255, verbose_name='Órgão/Autarquia')
    valor_recompensa = models.DecimalField(max_digits=10, decimal_places=2, default=50.00, verbose_name='Valor da Recompensa (R$)', help_text='Valor a ser pago por prova válida')
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='aberto',
        verbose_name='Status'
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        db_table = 'demandas'
        verbose_name = 'Concurso'
        verbose_name_plural = 'Concursos'
        ordering = ['-criado_em']
    
    def __str__(self):
        return f"{self.concurso} - {self.numero_edital}"
    
    @property
    def tem_prova_aprovada(self):
        """Verifica se já tem alguma prova aprovada/paga"""
        return self.tickets.filter(status__in=['pago', 'aprovado']).exists()
    
    @property
    def envios_pendentes(self):
        """Conta envios aguardando análise"""
        return self.tickets.filter(status__in=['aguardando', 'em_analise']).count()
