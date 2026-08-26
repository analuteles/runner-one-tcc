from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Ferias
from .serializers import FeriasSerializer


class FeriasViewSet(viewsets.ModelViewSet):
    """CRUD de períodos de férias dos motoristas."""

    queryset = Ferias.objects.select_related('motorista').all()
    serializer_class = FeriasSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['motorista']
    ordering_fields = ['data_inicio', 'data_fim']
