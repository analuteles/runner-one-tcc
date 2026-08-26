import datetime

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Motorista


class MotoristaTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='senha123')
        self.client.force_authenticate(user=self.user)

    def _dados_motorista(self, **sobrescreve):
        dados = {
            'nome': 'Carlos Pereira',
            'cpf': '11122233344',
            'telefone': '11955554444',
            'email': 'carlos@runnerone.com',
            'cnh_numero': '12345678900',
            'cnh_categoria': 'AB',
            'cnh_validade': (datetime.date.today() + datetime.timedelta(days=365)).isoformat(),
            'data_admissao': datetime.date.today().isoformat(),
        }
        dados.update(sobrescreve)
        return dados

    def test_criar_motorista(self):
        resposta = self.client.post('/api/motoristas/', self._dados_motorista())
        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)
        self.assertFalse(resposta.data['cnh_vencida'])

    def test_excluir_motorista_apenas_inativa(self):
        motorista = Motorista.objects.create(
            nome='Ana Lima', cpf='55566677788', telefone='11933332222',
            cnh_numero='99988877766', cnh_categoria='B',
            cnh_validade=datetime.date.today() + datetime.timedelta(days=100),
            data_admissao=datetime.date.today(),
        )
        resposta = self.client.delete(f'/api/motoristas/{motorista.id}/')
        self.assertEqual(resposta.status_code, status.HTTP_204_NO_CONTENT)
        motorista.refresh_from_db()
        self.assertFalse(motorista.ativo)

    def test_desempenho_sem_entregas_nao_gera_erro(self):
        motorista = Motorista.objects.create(
            nome='Pedro Costa', cpf='22233344455', telefone='11922223333',
            cnh_numero='11223344556', cnh_categoria='D',
            cnh_validade=datetime.date.today() + datetime.timedelta(days=200),
            data_admissao=datetime.date.today(),
        )
        resposta = self.client.get(f'/api/motoristas/{motorista.id}/desempenho/')
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data['total_entregas'], 0)
        self.assertEqual(resposta.data['produtividade_percentual'], 0.0)
