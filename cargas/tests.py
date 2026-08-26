import datetime

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from clientes.models import Cliente, TipoPessoa
from pedidos.models import Pedido, TipoCarga

from .models import Carga


class CargaTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='senha123')
        self.client.force_authenticate(user=self.user)
        cliente = Cliente.objects.create(
            tipo_pessoa=TipoPessoa.JURIDICA, nome='Indústria XYZ', cpf_cnpj='22333444000155',
            telefone='11955554444', endereco='Rua Industrial, 200', cidade='Guarulhos',
            estado='SP', cep='07000000',
        )
        self.pedido = Pedido.objects.create(
            cliente=cliente, origem='Guarulhos - SP', destino='Campinas - SP',
            tipo_carga=TipoCarga.GERAL,
            data_entrega_prevista=datetime.date.today() + datetime.timedelta(days=2),
        )

    def test_criar_carga(self):
        dados = {
            'pedido': self.pedido.id,
            'tipo_mercadoria': 'Eletrônicos',
            'peso_kg': '350.50',
            'volume_m3': '2.400',
        }
        resposta = self.client.post('/api/cargas/', dados)
        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)

    def test_nao_permite_duas_cargas_no_mesmo_pedido(self):
        Carga.objects.create(pedido=self.pedido, tipo_mercadoria='Móveis', peso_kg=100, volume_m3=1)
        dados = {
            'pedido': self.pedido.id,
            'tipo_mercadoria': 'Roupas',
            'peso_kg': '50.00',
            'volume_m3': '0.500',
        }
        resposta = self.client.post('/api/cargas/', dados)
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
