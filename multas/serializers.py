from rest_framework import serializers

from .models import Multa


class MultaSerializer(serializers.ModelSerializer):
    motorista_nome = serializers.CharField(source='motorista.nome', read_only=True)

    class Meta:
        model = Multa
        fields = [
            'id',
            'motorista',
            'motorista_nome',
            'veiculo',
            'motivo',
            'data',
            'valor',
            'observacao',
            'data_cadastro',
        ]
        read_only_fields = ['id', 'data_cadastro']
