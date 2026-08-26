from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Documento
from .serializers import DocumentoSerializer


class DocumentoViewSet(viewsets.ModelViewSet):
    """CRUD de documentos dos motoristas (CNH, exames, certidões etc.)."""

    queryset = Documento.objects.select_related('motorista').all()
    serializer_class = DocumentoSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['motorista', 'tipo_documento']
    ordering_fields = ['data_validade']
