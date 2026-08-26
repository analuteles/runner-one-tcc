from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Ocorrencia
from .serializers import OcorrenciaSerializer


class OcorrenciaViewSet(viewsets.ModelViewSet):
    """CRUD de ocorrências registradas durante as entregas."""

    queryset = Ocorrencia.objects.select_related('entrega').all()
    serializer_class = OcorrenciaSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['tipo', 'entrega']
    search_fields = ['descricao', 'observacao']
    ordering_fields = ['data']
