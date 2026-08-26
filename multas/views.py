from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Multa
from .serializers import MultaSerializer


class MultaViewSet(viewsets.ModelViewSet):
    """CRUD de multas, relacionadas a um motorista e, quando aplicável, a um veículo."""

    queryset = Multa.objects.select_related('motorista', 'veiculo').all()
    serializer_class = MultaSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['motorista', 'veiculo']
    search_fields = ['motivo', 'observacao']
    ordering_fields = ['data', 'valor']
