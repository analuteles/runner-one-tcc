from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Motorista
from .serializers import MotoristaSerializer
from .services import calcular_desempenho


class MotoristaViewSet(viewsets.ModelViewSet):
    """
    CRUD de motoristas, além de rotas extras para consultar o
    histórico de entregas, o desempenho, a documentação e as férias
    de um motorista específico.
    """

    queryset = Motorista.objects.all()
    serializer_class = MotoristaSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['ativo', 'cnh_categoria']
    search_fields = ['nome', 'cpf', 'cnh_numero']
    ordering_fields = ['nome', 'data_admissao']

    def perform_destroy(self, instance):
        # "Excluir" um motorista, na prática, apenas o inativa —
        # preserva o histórico de entregas já realizadas por ele.
        instance.ativo = False
        instance.save(update_fields=['ativo'])

    @action(detail=True, methods=['get'])
    def entregas(self, request, pk=None):
        """GET /api/motoristas/{id}/entregas/ — histórico de entregas do motorista."""
        from entregas.models import Entrega
        from entregas.serializers import EntregaSerializer

        motorista = self.get_object()
        entregas_qs = Entrega.objects.filter(motorista=motorista).select_related(
            'pedido', 'pedido__cliente', 'motorista', 'veiculo'
        )

        status_param = request.query_params.get('status')
        if status_param:
            entregas_qs = entregas_qs.filter(status=status_param.upper())

        data_inicio = request.query_params.get('data_inicio')
        if data_inicio:
            entregas_qs = entregas_qs.filter(data_prevista__gte=data_inicio)

        data_fim = request.query_params.get('data_fim')
        if data_fim:
            entregas_qs = entregas_qs.filter(data_prevista__lte=data_fim)

        entregas_qs = entregas_qs.order_by('-data_prevista')

        page = self.paginate_queryset(entregas_qs)
        if page is not None:
            serializer = EntregaSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = EntregaSerializer(entregas_qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def desempenho(self, request, pk=None):
        """GET /api/motoristas/{id}/desempenho/ — indicadores simples de desempenho."""
        motorista = self.get_object()
        return Response(calcular_desempenho(motorista))

    @action(detail=True, methods=['get'])
    def documentos(self, request, pk=None):
        """GET /api/motoristas/{id}/documentos/ — documentos cadastrados do motorista."""
        from documentos.models import Documento
        from documentos.serializers import DocumentoSerializer

        motorista = self.get_object()
        documentos_qs = Documento.objects.filter(motorista=motorista).order_by('-data_validade')
        serializer = DocumentoSerializer(documentos_qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def ferias(self, request, pk=None):
        """GET /api/motoristas/{id}/ferias/ — períodos de férias do motorista."""
        from ferias.models import Ferias
        from ferias.serializers import FeriasSerializer

        motorista = self.get_object()
        ferias_qs = Ferias.objects.filter(motorista=motorista).order_by('-data_inicio')
        serializer = FeriasSerializer(ferias_qs, many=True)
        return Response(serializer.data)
