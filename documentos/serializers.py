from rest_framework import serializers

from .models import Documento


class DocumentoSerializer(serializers.ModelSerializer):
    motorista_nome = serializers.CharField(source='motorista.nome', read_only=True)
    situacao = serializers.CharField(read_only=True)

    class Meta:
        model = Documento
        fields = [
            'id',
            'motorista',
            'motorista_nome',
            'tipo_documento',
            'numero',
            'data_emissao',
            'data_validade',
            'situacao',
            'observacao',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        data_emissao = attrs.get('data_emissao', getattr(self.instance, 'data_emissao', None))
        data_validade = attrs.get('data_validade', getattr(self.instance, 'data_validade', None))
        if data_emissao and data_validade and data_validade < data_emissao:
            raise serializers.ValidationError(
                {'data_validade': 'A data de validade não pode ser anterior à data de emissão.'}
            )
        return attrs
