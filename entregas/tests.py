import datetime

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from clientes.models import Cliente, TipoPessoa
from motoristas.models import Motorista
from pedidos.models import Pedido, TipoCarga
from veiculos.models import SituacaoVeiculo, Veiculo

from .models import Entrega, StatusEntrega


class EntregaTestCaseBase(APITestCase):
    """Prepara os dados básicos (cliente, motoristas, veículos, pedido) usados nos testes abaixo."""

    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='senha123')
        self.client.force_authenticate(user=self.user)

        self.cliente = Cliente.objects.create(
            tipo_pessoa=TipoPessoa.JURIDICA, nome='Loja Central', cpf_cnpj='33444555000166',
            telefone='11944443333', endereco='Rua Central, 10', cidade='São Paulo',
            estado='SP', cep='01000000',
        )
        self.motorista = Motorista.objects.create(
            nome='José Andrade', cpf='44455566677', telefone='11933332222',
            cnh_numero='55566677788', cnh_categoria='D',
            cnh_validade=datetime.date.today() + datetime.timedelta(days=300),
            data_admissao=datetime.date.today(), ativo=True,
        )
        self.motorista_inativo = Motorista.objects.create(
            nome='Motorista Inativo', cpf='99988877766', telefone='11911112222',
            cnh_numero='11122233344', cnh_categoria='B',
            cnh_validade=datetime.date.today() + datetime.timedelta(days=300),
            data_admissao=datetime.date.today(), ativo=False,
        )
        self.veiculo = Veiculo.objects.create(
            placa='ABC1234', modelo='Sprinter', marca='Mercedes-Benz', ano=2021,
            capacidade_carga_kg=1500, situacao=SituacaoVeiculo.DISPONIVEL,
        )
        self.veiculo_em_manutencao = Veiculo.objects.create(
            placa='DEF5678', modelo='Daily', marca='Iveco', ano=2019,
            capacidade_carga_kg=2000, situacao=SituacaoVeiculo.MANUTENCAO,
        )
        self.pedido = Pedido.objects.create(
            cliente=self.cliente, origem='São Paulo - SP', destino='Santos - SP',
            tipo_carga=TipoCarga.GERAL,
            data_entrega_prevista=datetime.date.today() + datetime.timedelta(days=1),
        )

    def _criar_entrega(self, **extra):
        dados = {'pedido': self.pedido.id}
        dados.update(extra)
        return self.client.post('/api/entregas/', dados)


class EntregaCriacaoTestCase(EntregaTestCaseBase):
    def test_criar_entrega_status_inicial_aguardando(self):
        resposta = self._criar_entrega()
        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resposta.data['status'], StatusEntrega.AGUARDANDO)
        # data_prevista deve ser herdada do pedido, já que não foi enviada explicitamente
        self.assertEqual(
            resposta.data['data_prevista'], self.pedido.data_entrega_prevista.isoformat()
        )

    def test_nao_permite_duas_entregas_ativas_no_mesmo_pedido(self):
        primeira = self._criar_entrega()
        self.assertEqual(primeira.status_code, status.HTTP_201_CREATED)

        segunda = self._criar_entrega()
        self.assertEqual(segunda.status_code, status.HTTP_400_BAD_REQUEST)

    def test_nova_entrega_e_permitida_apos_cancelamento_da_anterior(self):
        primeira = self._criar_entrega()
        self.client.post(f"/api/entregas/{primeira.data['id']}/cancelar/", {'motivo': 'Teste'})

        segunda = self._criar_entrega()
        self.assertEqual(segunda.status_code, status.HTTP_201_CREATED)

    def test_associar_motorista_inativo_na_criacao_e_bloqueado(self):
        resposta = self._criar_entrega(motorista=self.motorista_inativo.id, veiculo=self.veiculo.id)
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('motorista', resposta.data)

    def test_associar_veiculo_indisponivel_na_criacao_e_bloqueado(self):
        resposta = self._criar_entrega(
            motorista=self.motorista.id, veiculo=self.veiculo_em_manutencao.id
        )
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('veiculo', resposta.data)


class EntregaFluxoTestCase(EntregaTestCaseBase):
    """Testa o fluxo AGUARDANDO -> EM_ROTA -> ENTREGUE, e o cancelamento."""

    def setUp(self):
        super().setUp()
        resposta = self._criar_entrega()
        self.entrega_id = resposta.data['id']

    def _atribuir_motorista_e_veiculo(self):
        return self.client.patch(
            f'/api/entregas/{self.entrega_id}/',
            {'motorista': self.motorista.id, 'veiculo': self.veiculo.id},
        )

    def _iniciar(self):
        return self.client.post(f'/api/entregas/{self.entrega_id}/iniciar/')

    def _finalizar(self):
        return self.client.post(f'/api/entregas/{self.entrega_id}/finalizar/')

    def _cancelar(self, motivo='Cliente desistiu do pedido'):
        return self.client.post(f'/api/entregas/{self.entrega_id}/cancelar/', {'motivo': motivo})

    def test_nao_permite_iniciar_sem_motorista_e_veiculo(self):
        resposta = self._iniciar()
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_iniciar_entrega_com_sucesso(self):
        self._atribuir_motorista_e_veiculo()
        resposta = self._iniciar()
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data['data']['status'], StatusEntrega.EM_ROTA)
        self.assertIsNotNone(resposta.data['data']['hora_saida'])

        self.veiculo.refresh_from_db()
        self.assertEqual(self.veiculo.situacao, SituacaoVeiculo.EM_USO)

    def test_nao_permite_iniciar_entrega_ja_em_rota(self):
        self._atribuir_motorista_e_veiculo()
        self._iniciar()
        segunda_tentativa = self._iniciar()
        self.assertEqual(segunda_tentativa.status_code, status.HTTP_400_BAD_REQUEST)

    def test_nao_permite_trocar_motorista_apos_entrega_em_rota(self):
        self._atribuir_motorista_e_veiculo()
        self._iniciar()

        outro_motorista = Motorista.objects.create(
            nome='Outro Motorista', cpf='12312312312', telefone='11900001111',
            cnh_numero='99988877700', cnh_categoria='B',
            cnh_validade=datetime.date.today() + datetime.timedelta(days=300),
            data_admissao=datetime.date.today(), ativo=True,
        )
        resposta = self.client.patch(
            f'/api/entregas/{self.entrega_id}/', {'motorista': outro_motorista.id}
        )
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_finalizar_entrega_com_sucesso_libera_veiculo(self):
        self._atribuir_motorista_e_veiculo()
        self._iniciar()
        resposta = self._finalizar()
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data['data']['status'], StatusEntrega.ENTREGUE)
        self.assertIsNotNone(resposta.data['data']['hora_chegada'])

        self.veiculo.refresh_from_db()
        self.assertEqual(self.veiculo.situacao, SituacaoVeiculo.DISPONIVEL)

    def test_nao_permite_finalizar_entrega_ainda_aguardando(self):
        resposta = self._finalizar()
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cancelar_entrega_exige_motivo(self):
        resposta = self.client.post(f'/api/entregas/{self.entrega_id}/cancelar/', {})
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cancelar_entrega_com_sucesso(self):
        resposta = self._cancelar('Endereço não localizado')
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data['data']['status'], StatusEntrega.CANCELADA)

    def test_nao_permite_finalizar_entrega_cancelada(self):
        self._cancelar()
        resposta = self._finalizar()
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_nao_permite_cancelar_entrega_ja_entregue(self):
        self._atribuir_motorista_e_veiculo()
        self._iniciar()
        self._finalizar()
        resposta = self._cancelar()
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_nao_permite_reverter_status_via_patch_direto(self):
        # "status" é somente leitura no serializer — só muda pelas ações dedicadas.
        resposta = self.client.patch(
            f'/api/entregas/{self.entrega_id}/', {'status': StatusEntrega.ENTREGUE}
        )
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        entrega = Entrega.objects.get(id=self.entrega_id)
        self.assertEqual(entrega.status, StatusEntrega.AGUARDANDO)  # não deve ter mudado

    def test_excluir_entrega_nao_e_permitido(self):
        resposta = self.client.delete(f'/api/entregas/{self.entrega_id}/')
        self.assertEqual(resposta.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class EntregaAtrasoTestCase(EntregaTestCaseBase):
    def test_entrega_e_marcada_como_atrasada_automaticamente(self):
        pedido_atrasado = Pedido.objects.create(
            cliente=self.cliente, origem='São Paulo - SP', destino='Sorocaba - SP',
            data_entrega_prevista=datetime.date.today() - datetime.timedelta(days=2),
        )
        entrega = Entrega.objects.create(
            pedido=pedido_atrasado, data_prevista=pedido_atrasado.data_entrega_prevista,
        )
        self.assertEqual(entrega.status, StatusEntrega.AGUARDANDO)  # ainda não foi recalculado

        resposta = self.client.get(f'/api/entregas/{entrega.id}/')
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data['status'], StatusEntrega.ATRASADA)

    def test_entrega_atrasada_ainda_pode_ser_iniciada_e_finalizada(self):
        pedido_atrasado = Pedido.objects.create(
            cliente=self.cliente, origem='São Paulo - SP', destino='Sorocaba - SP',
            data_entrega_prevista=datetime.date.today() - datetime.timedelta(days=1),
        )
        entrega = Entrega.objects.create(
            pedido=pedido_atrasado, motorista=self.motorista, veiculo=self.veiculo,
            data_prevista=pedido_atrasado.data_entrega_prevista,
        )

        resposta_iniciar = self.client.post(f'/api/entregas/{entrega.id}/iniciar/')
        self.assertEqual(resposta_iniciar.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta_iniciar.data['data']['status'], StatusEntrega.EM_ROTA)

        resposta_finalizar = self.client.post(f'/api/entregas/{entrega.id}/finalizar/')
        self.assertEqual(resposta_finalizar.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta_finalizar.data['data']['status'], StatusEntrega.ENTREGUE)
