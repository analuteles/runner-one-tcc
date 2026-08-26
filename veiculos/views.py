from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import SituacaoVeiculo, Veiculo
from .serializers import VeiculoSerializer


class VeiculoViewSet(viewsets.ModelViewSet):
    """
    CRUD de veículos.

    A situação do veículo (disponível / em uso / manutenção / inativo)
    também é atualizada automaticamente pelo módulo de entregas quando
    uma entrega é iniciada, finalizada ou cancelada.
    """

    queryset = Veiculo.objects.all()
    serializer_class = VeiculoSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['situacao']
    search_fields = ['placa', 'modelo', 'marca']
    ordering_fields = ['placa', 'ano']

    def perform_destroy(self, instance):
        # "Excluir" um veículo, na prática, apenas o marca como inativo.
        instance.situacao = SituacaoVeiculo.INATIVO
        instance.save(update_fields=['situacao'])
