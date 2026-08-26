import datetime

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from clientes.models import Cliente, TipoPessoa
from entregas.models import Entrega, StatusEntrega
from motoristas.models import Motorista
from pedidos.models import Pedido
from veiculos.models import SituacaoVeiculo, Veiculo


class RelatorioTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='senha123')
        self.client.force_authenticate(user=self.user)

        self.cliente = Cliente.objects.create(
            tipo_pessoa=TipoPessoa.JURIDICA, nome='Distribuidora Norte', cpf_cnpj='90807060000122',
            telefone='11911119999', endereco='Rua Norte, 300', cidade='São Paulo',
            estado='SP', cep='03000000',
        )
        self.motorista = Motorista.objects.create(
            nome='Vitor Nunes', cpf='11223344550', telefone='11988889999',
            cnh_numero='99887766554', cnh_categoria='D',
            cnh_validade=datetime.date.today() + datetime.timedelta(days=300),
            data_admissao=datetime.date.today(),
        )
        self.veiculo = Veiculo.objects.create(
            placa='GHI9J87', modelo='Sprinter', marca='Mercedes-Benz', ano=2020,
            capacidade_carga_kg=1200, situacao=SituacaoVeiculo.DISPONIVEL,
        )

        hoje = datetime.date.today()

        pedido_entregue = Pedido.objects.create(
            cliente=self.cliente, origem='São Paulo - SP', destino='Suzano - SP',
            data_entrega_prevista=hoje, valor_frete=500,
        )
        Entrega.objects.create(
            pedido=pedido_entregue, motorista=self.motorista, veiculo=self.veiculo,
            data_prevista=hoje, status=StatusEntrega.ENTREGUE, hora_chegada=timezone.now(),
        )

        pedido_pendente = Pedido.objects.create(
            cliente=self.cliente, origem='São Paulo - SP', destino='Mauá - SP',
            data_entrega_prevista=hoje, valor_frete=300,
        )
        Entrega.objects.create(pedido=pedido_pendente, data_prevista=hoje)

    def test_relatorio_entregas_do_dia(self):
        resposta = self.client.get('/api/relatorios/entregas/?periodo=dia')
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data['total_entregas'], 2)

    def test_relatorio_desempenho(self):
        resposta = self.client.get('/api/relatorios/desempenho/')
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        nomes = [motorista['motorista_nome'] for motorista in resposta.data['motoristas']]
        self.assertIn('Vitor Nunes', nomes)

    def test_relatorio_faturamento_considera_apenas_entregas_concluidas(self):
        resposta = self.client.get('/api/relatorios/faturamento/?periodo=dia')
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data['quantidade_entregas_faturadas'], 1)
        self.assertEqual(float(resposta.data['valor_total_faturado']), 500.0)
