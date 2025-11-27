from django.contrib import admin
from .models import Demanda


@admin.register(Demanda)
class DemandaAdmin(admin.ModelAdmin):
    """
    Configuração do admin para Demanda.
    """
    list_display = ['concurso', 'numero_edital', 'banca', 'cargo', 'data_concurso', 'status', 'criado_em']
    list_filter = ['status', 'banca', 'data_concurso']
    search_fields = ['concurso', 'numero_edital', 'cargo', 'autarquia']
    ordering = ['-criado_em']
    date_hierarchy = 'criado_em'
    
    fieldsets = (
        ('Informações do Concurso', {
            'fields': ('concurso', 'numero_edital', 'banca', 'cargo', 'autarquia')
        }),
        ('Detalhes', {
            'fields': ('data_concurso', 'status')
        }),
    )
