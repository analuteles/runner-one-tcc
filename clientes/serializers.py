from rest_framework import serializers

from .models import Cliente, TipoPessoa


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = [
            'id',
            'tipo_pessoa',
            'nome',
            'cpf_cnpj',
            'telefone',
            'email',
            'endereco',
            'cidade',
            'estado',
            'cep',
            'ativo',
            'data_cadastro',
            'data_atualizacao',
        ]
        read_only_fields = ['id', 'data_cadastro', 'data_atualizacao']

    def validate_cpf_cnpj(self, valor):
        if not valor.isdigit():
            raise serializers.ValidationError('O CPF/CNPJ deve conter apenas números.')
        return valor

    def validate_estado(self, valor):
        return valor.upper()

    def validate(self, attrs):
        # Usa o valor já enviado na requisição, ou o valor atual do
        # registro (em caso de PATCH parcial, sem esse campo).
        tipo_pessoa = attrs.get('tipo_pessoa', getattr(self.instance, 'tipo_pessoa', None))
        cpf_cnpj = attrs.get('cpf_cnpj', getattr(self.instance, 'cpf_cnpj', ''))

        if tipo_pessoa == TipoPessoa.FISICA and len(cpf_cnpj) != 11:
            raise serializers.ValidationError({'cpf_cnpj': 'CPF deve conter 11 dígitos.'})
        if tipo_pessoa == TipoPessoa.JURIDICA and len(cpf_cnpj) != 14:
            raise serializers.ValidationError({'cpf_cnpj': 'CNPJ deve conter 14 dígitos.'})
        return attrs
