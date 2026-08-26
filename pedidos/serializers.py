from rest_framework import serializers

from .models import Pedido


class PedidoSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.CharField(source='cliente.nome', read_only=True)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Pedido
        fields = [
            'id',
            'cliente',
            'cliente_nome',
            'origem',
            'destino',
            'tipo_carga',
            'data_pedido',
            'data_entrega_prevista',
            'valor_frete',
            'observacoes',
            'status',
        ]
        read_only_fields = ['id', 'data_pedido']

    def validate_cliente(self, cliente):
        if not cliente.ativo:
            raise serializers.ValidationError(
                'Não é possível abrir um pedido para um cliente inativo.'
            )
        return cliente
