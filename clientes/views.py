from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Cliente
from .serializers import ClienteSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    """
    CRUD de clientes.

    list: Lista os clientes cadastrados (aceita busca e paginação).
    create: Cadastra um novo cliente.
    retrieve: Consulta um cliente específico.
    update / partial_update: Edita os dados de um cliente.
    destroy: Inativa o cliente (não apaga o histórico do banco de dados).
    """

    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['ativo', 'tipo_pessoa', 'cidade', 'estado']
    search_fields = ['nome', 'cpf_cnpj', 'email']
    ordering_fields = ['nome', 'data_cadastro']

    def perform_destroy(self, instance):
        # "Excluir" um cliente, na prática, apenas o inativa.
        # Isso preserva o histórico de pedidos/entregas já vinculados.
        instance.ativo = False
        instance.save(update_fields=['ativo'])
