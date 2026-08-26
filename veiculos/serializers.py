from rest_framework import serializers

from .models import Veiculo


class VeiculoSerializer(serializers.ModelSerializer):
    disponivel = serializers.BooleanField(read_only=True)

    class Meta:
        model = Veiculo
        fields = [
            'id',
            'placa',
            'modelo',
            'marca',
            'ano',
            'capacidade_carga_kg',
            'situacao',
            'disponivel',
            'data_cadastro',
            'data_atualizacao',
        ]
        read_only_fields = ['id', 'data_cadastro', 'data_atualizacao']

    def validate_placa(self, valor):
        return valor.upper().replace('-', '').replace(' ', '')
