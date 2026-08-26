from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Carga
from .serializers import CargaSerializer


class CargaViewSet(viewsets.ModelViewSet):
    """CRUD de cargas (mercadoria transportada em cada pedido)."""

    queryset = Carga.objects.select_related('pedido').all()
    serializer_class = CargaSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['pedido']
    search_fields = ['tipo_mercadoria']
