from rest_framework import serializers

from .models import Ocorrencia


class OcorrenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ocorrencia
        fields = ['id', 'entrega', 'tipo', 'descricao', 'data', 'observacao']
        read_only_fields = ['id']
