from rest_framework import serializers

from .models import Motorista


class MotoristaSerializer(serializers.ModelSerializer):
    cnh_vencida = serializers.BooleanField(read_only=True)

    class Meta:
        model = Motorista
        fields = [
            'id',
            'nome',
            'cpf',
            'telefone',
            'email',
            'cnh_numero',
            'cnh_categoria',
            'cnh_validade',
            'cnh_vencida',
            'data_admissao',
            'ativo',
            'data_cadastro',
            'data_atualizacao',
        ]
        read_only_fields = ['id', 'data_cadastro', 'data_atualizacao']

    def validate_cpf(self, valor):
        if not valor.isdigit():
            raise serializers.ValidationError('O CPF deve conter apenas números.')
        return valor
