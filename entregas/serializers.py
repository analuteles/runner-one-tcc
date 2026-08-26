from rest_framework import serializers

from veiculos.models import SituacaoVeiculo

from .models import Entrega, StatusEntrega


class EntregaSerializer(serializers.ModelSerializer):
    # Campos derivados (somente leitura) para facilitar o consumo da
    # API: quem for montar uma tela de entregas não precisa fazer
    # consultas extras só para saber o nome do cliente, a origem, o
    # destino etc. — tudo isso já vem do pedido relacionado.
    cliente_nome = serializers.CharField(source='pedido.cliente.nome', read_only=True)
    origem = serializers.CharField(source='pedido.origem', read_only=True)
    destino = serializers.CharField(source='pedido.destino', read_only=True)
    tipo_carga = serializers.CharField(source='pedido.tipo_carga', read_only=True)
    tipo_mercadoria = serializers.CharField(
        source='pedido.carga.tipo_mercadoria', read_only=True, default=None
    )
    motorista_nome = serializers.SerializerMethodField()
    veiculo_placa = serializers.SerializerMethodField()

    class Meta:
        model = Entrega
        fields = [
            'id',
            'pedido',
            'cliente_nome',
            'motorista',
            'motorista_nome',
            'veiculo',
            'veiculo_placa',
            'origem',
            'destino',
            'tipo_carga',
            'tipo_mercadoria',
            'status',
            'data_prevista',
            'hora_saida',
            'hora_chegada',
            'motivo_cancelamento',
            'data_criacao',
            'data_atualizacao',
        ]
        # status, horários e motivo de cancelamento só mudam através das
        # ações dedicadas (iniciar/finalizar/cancelar) — não por um PUT/PATCH
        # genérico. Isso mantém as regras de negócio concentradas no model.
        read_only_fields = [
            'id',
            'status',
            'hora_saida',
            'hora_chegada',
            'motivo_cancelamento',
            'data_criacao',
            'data_atualizacao',
        ]
        extra_kwargs = {
            # Se não vier no payload, assume a data prevista do próprio
            # pedido (ver create() logo abaixo) — evita ter que repetir
            # a mesma data em dois lugares na hora de abrir a entrega.
            'data_prevista': {'required': False},
        }

    def create(self, validated_data):
        if not validated_data.get('data_prevista'):
            validated_data['data_prevista'] = validated_data['pedido'].data_entrega_prevista
        return super().create(validated_data)

    def get_motorista_nome(self, obj):
        return obj.motorista.nome if obj.motorista else None

    def get_veiculo_placa(self, obj):
        return obj.veiculo.placa if obj.veiculo else None

    def validate_pedido(self, pedido):
        if self.instance is None:
            # Criação: evita duas entregas "ativas" ao mesmo tempo para o mesmo pedido.
            existe_entrega_ativa = pedido.entregas.exclude(status=StatusEntrega.CANCELADA).exists()
            if existe_entrega_ativa:
                raise serializers.ValidationError(
                    'Este pedido já possui uma entrega em andamento ou concluída.'
                )
        elif pedido != self.instance.pedido:
            # Atualização: não faz sentido trocar o pedido de uma entrega já criada.
            raise serializers.ValidationError(
                'Não é possível alterar o pedido de uma entrega já criada.'
            )
        return pedido

    def validate(self, attrs):
        instance = self.instance

        motorista_novo = attrs.get('motorista', instance.motorista if instance else None)
        veiculo_novo = attrs.get('veiculo', instance.veiculo if instance else None)

        motorista_mudou = 'motorista' in attrs and (
            instance is None or attrs['motorista'] != instance.motorista
        )
        veiculo_mudou = 'veiculo' in attrs and (
            instance is None or attrs['veiculo'] != instance.veiculo
        )

        # Regra 3: motorista inativo não pode ser associado a uma nova entrega.
        if motorista_mudou and motorista_novo is not None and not motorista_novo.ativo:
            raise serializers.ValidationError(
                {'motorista': 'Motorista inativo não pode ser associado a uma nova entrega.'}
            )

        # Regra 4: veículo indisponível não pode ser associado a uma nova entrega.
        if (
            veiculo_mudou
            and veiculo_novo is not None
            and veiculo_novo.situacao != SituacaoVeiculo.DISPONIVEL
        ):
            raise serializers.ValidationError(
                {'veiculo': 'Veículo indisponível não pode ser associado a uma nova entrega.'}
            )

        # Depois que a entrega sai do status AGUARDANDO, motorista e
        # veículo não podem mais ser trocados por aqui — apenas pelas
        # ações dedicadas (cancelar + nova entrega, se for o caso).
        if instance and instance.status != StatusEntrega.AGUARDANDO:
            if motorista_mudou or veiculo_mudou:
                raise serializers.ValidationError(
                    'Não é possível alterar motorista ou veículo de uma entrega que '
                    'já saiu, foi concluída, cancelada ou está atrasada.'
                )

        return attrs


class CancelarEntregaSerializer(serializers.Serializer):
    """Usado apenas pela ação de cancelamento — exige o motivo do cancelamento."""

    motivo = serializers.CharField(max_length=500, allow_blank=False)
