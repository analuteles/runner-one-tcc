from rest_framework import serializers

from .models import Carga


class CargaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carga
        fields = ['id', 'pedido', 'tipo_mercadoria', 'peso_kg', 'volume_m3', 'descricao']
        read_only_fields = ['id']

    def validate_pedido(self, pedido):
        # O campo já é OneToOne no banco; validar aqui só gera uma
        # mensagem de erro mais amigável do que o erro genérico do banco.
        if self.instance is None and hasattr(pedido, 'carga'):
            raise serializers.ValidationError('Este pedido já possui uma carga cadastrada.')
        return pedido
