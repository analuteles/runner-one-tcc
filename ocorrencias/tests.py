import datetime

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from clientes.models import Cliente, TipoPessoa
from entregas.models import Entrega
from pedidos.models import Pedido

from .models import Ocorrencia, TipoOcorrencia


class OcorrenciaTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='senha123')
        self.client.force_authenticate(user=self.user)

        cliente = Cliente.objects.create(
            tipo_pessoa=TipoPessoa.FISICA, nome='Fernanda Alves', cpf_cnpj='10203040506',
            telefone='11922221111', endereco='Rua das Flores, 55', cidade='São Paulo',
            estado='SP', cep='02000000',
        )
        pedido = Pedido.objects.create(
            cliente=cliente, origem='São Paulo - SP', destino='Niterói - RJ',
            data_entrega_prevista=datetime.date.today() + datetime.timedelta(days=4),
        )
        self.entrega = Entrega.objects.create(
            pedido=pedido, data_prevista=pedido.data_entrega_prevista
        )

    def test_criar_ocorrencia(self):
        dados = {
            'entrega': self.entrega.id,
            'tipo': TipoOcorrencia.ENDERECO_INCORRETO,
            'descricao': 'Endereço informado pelo cliente não foi encontrado.',
        }
        resposta = self.client.post('/api/ocorrencias/', dados)
        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)

    def test_listar_ocorrencias_de_uma_entrega(self):
        Ocorrencia.objects.create(
            entrega=self.entrega, tipo=TipoOcorrencia.ATRASO, descricao='Trânsito intenso na via.',
        )
        resposta = self.client.get(f'/api/entregas/{self.entrega.id}/ocorrencias/')
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resposta.data), 1)
