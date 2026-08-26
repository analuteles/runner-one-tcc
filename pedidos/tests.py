import datetime

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from clientes.models import Cliente, TipoPessoa

from .models import StatusPedido, TipoCarga


class PedidoTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='senha123')
        self.client.force_authenticate(user=self.user)
        self.cliente = Cliente.objects.create(
            tipo_pessoa=TipoPessoa.JURIDICA, nome='Comércio ABC', cpf_cnpj='11222333000144',
            telefone='11966665555', endereco='Av. Principal, 500', cidade='São Paulo',
            estado='SP', cep='04567000',
        )

    def test_criar_pedido(self):
        dados = {
            'cliente': self.cliente.id,
            'origem': 'São Paulo - SP',
            'destino': 'Rio de Janeiro - RJ',
            'tipo_carga': TipoCarga.GERAL,
            'data_entrega_prevista': (datetime.date.today() + datetime.timedelta(days=3)).isoformat(),
            'valor_frete': '850.00',
        }
        resposta = self.client.post('/api/pedidos/', dados)
        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resposta.data['status'], StatusPedido.ABERTO)

    def test_pedido_para_cliente_inativo_e_bloqueado(self):
        self.cliente.ativo = False
        self.cliente.save()
        dados = {
            'cliente': self.cliente.id,
            'origem': 'São Paulo - SP',
            'destino': 'Curitiba - PR',
            'data_entrega_prevista': (datetime.date.today() + datetime.timedelta(days=2)).isoformat(),
        }
        resposta = self.client.post('/api/pedidos/', dados)
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
