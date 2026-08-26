from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Pedido
from .serializers import PedidoSerializer


class PedidoViewSet(viewsets.ModelViewSet):
    """
    CRUD de pedidos de entrega (a solicitação feita pelo cliente).

    A execução do pedido em si é controlada separadamente pelo módulo
    de entregas — ver /api/entregas/.
    """

    queryset = Pedido.objects.select_related('cliente').all()
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['cliente', 'tipo_carga']
    search_fields = ['origem', 'destino']
    ordering_fields = ['data_pedido', 'data_entrega_prevista']
