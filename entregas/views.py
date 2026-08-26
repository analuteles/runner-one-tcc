from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Entrega
from .serializers import CancelarEntregaSerializer, EntregaSerializer


class EntregaViewSet(viewsets.ModelViewSet):
    """
    CRUD de entregas (a execução de um pedido), além das rotas de ação
    para iniciar, finalizar e cancelar uma entrega, e para consultar
    as ocorrências relacionadas a ela.
    """

    queryset = Entrega.objects.all()
    serializer_class = EntregaSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'motorista', 'veiculo', 'pedido']
    ordering_fields = ['data_prevista', 'data_criacao']

    def get_queryset(self):
        # Antes de listar/consultar, atualiza quem já passou da data
        # prevista para ATRASADA. Ver EntregaQuerySet.atualizar_atrasadas.
        Entrega.objects.atualizar_atrasadas()

        queryset = Entrega.objects.select_related(
            'pedido', 'pedido__cliente', 'pedido__carga', 'motorista', 'veiculo'
        ).all()

        data_inicio = self.request.query_params.get('data_inicio')
        if data_inicio:
            queryset = queryset.filter(data_prevista__gte=data_inicio)

        data_fim = self.request.query_params.get('data_fim')
        if data_fim:
            queryset = queryset.filter(data_prevista__lte=data_fim)

        return queryset

    def destroy(self, request, *args, **kwargs):
        # Entregas não são excluídas de verdade: isso apagaria o
        # histórico de operações da transportadora. Quem quiser
        # "remover" uma entrega deve usar a ação de cancelamento.
        return Response(
            {
                'detail': (
                    'Entregas não podem ser excluídas. '
                    'Utilize a ação de cancelamento (POST /cancelar/).'
                )
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @action(detail=True, methods=['post'])
    def iniciar(self, request, pk=None):
        """POST /api/entregas/{id}/iniciar/ — registra a saída e muda o status para EM_ROTA."""
        entrega = self.get_object()
        entrega.iniciar()
        return Response(
            {
                'message': 'Entrega iniciada com sucesso.',
                'data': EntregaSerializer(entrega).data,
            }
        )

    @action(detail=True, methods=['post'])
    def finalizar(self, request, pk=None):
        """POST /api/entregas/{id}/finalizar/ — registra a chegada e conclui a entrega."""
        entrega = self.get_object()
        entrega.finalizar()
        return Response(
            {
                'message': 'Entrega finalizada com sucesso.',
                'data': EntregaSerializer(entrega).data,
            }
        )

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """POST /api/entregas/{id}/cancelar/ — cancela a entrega (exige motivo)."""
        entrada = CancelarEntregaSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)

        entrega = self.get_object()
        entrega.cancelar(entrada.validated_data['motivo'])
        return Response(
            {
                'message': 'Entrega cancelada com sucesso.',
                'data': EntregaSerializer(entrega).data,
            }
        )

    @action(detail=True, methods=['get'])
    def ocorrencias(self, request, pk=None):
        """GET /api/entregas/{id}/ocorrencias/ — ocorrências registradas para esta entrega."""
        from ocorrencias.models import Ocorrencia
        from ocorrencias.serializers import OcorrenciaSerializer

        entrega = self.get_object()
        ocorrencias_qs = Ocorrencia.objects.filter(entrega=entrega).order_by('-data')
        serializer = OcorrenciaSerializer(ocorrencias_qs, many=True)
        return Response(serializer.data)
