from rest_framework import serializers
from .models import Demanda


class DemandaSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Demanda.
    """
    
    class Meta:
        model = Demanda
        fields = ['id', 'concurso', 'numero_edital', 'banca', 'data_concurso',
                  'cargo', 'autarquia', 'status', 'criado_em', 'atualizado_em']
        read_only_fields = ['id', 'criado_em', 'atualizado_em']
