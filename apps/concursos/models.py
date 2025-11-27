from django.db import models


class Demanda(models.Model):
    """
    Modelo para gerenciar demandas de concursos públicos.
    Cada demanda representa um concurso/edital específico.
    """
    
    STATUS_CHOICES = [
        ('aberta', 'Aberta'),
        ('em_andamento', 'Em Andamento'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
    ]
    
    concurso = models.CharField(max_length=255, verbose_name='Nome do Concurso')
    numero_edital = models.CharField(max_length=50, verbose_name='Número do Edital')
    banca = models.CharField(max_length=100, verbose_name='Banca Examinadora')
    data_concurso = models.DateField(verbose_name='Data do Concurso')
    cargo = models.CharField(max_length=255, verbose_name='Cargo')
    autarquia = models.CharField(max_length=255, verbose_name='Órgão/Autarquia')
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='aberta',
        verbose_name='Status'
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        db_table = 'demandas'
        verbose_name = 'Demanda'
        verbose_name_plural = 'Demandas'
        ordering = ['-criado_em']
    
    def __str__(self):
        return f"{self.concurso} - {self.numero_edital}"
