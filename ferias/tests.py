import datetime

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from motoristas.models import Motorista

from .models import Ferias, SituacaoFerias


class FeriasTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='senha123')
        self.client.force_authenticate(user=self.user)
        self.motorista = Motorista.objects.create(
            nome='Bruno Martins', cpf='70809101112', telefone='11933334444',
            cnh_numero='80910111213', cnh_categoria='D',
            cnh_validade=datetime.date.today() + datetime.timedelta(days=200),
            data_admissao=datetime.date.today(),
        )

    def test_criar_ferias(self):
        dados = {
            'motorista': self.motorista.id,
            'data_inicio': (datetime.date.today() + datetime.timedelta(days=10)).isoformat(),
            'data_fim': (datetime.date.today() + datetime.timedelta(days=20)).isoformat(),
        }
        resposta = self.client.post('/api/ferias/', dados)
        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resposta.data['situacao'], SituacaoFerias.AGENDADA)

    def test_ferias_sobrepostas_sao_bloqueadas(self):
        Ferias.objects.create(
            motorista=self.motorista,
            data_inicio=datetime.date.today() + datetime.timedelta(days=10),
            data_fim=datetime.date.today() + datetime.timedelta(days=20),
        )
        dados = {
            'motorista': self.motorista.id,
            'data_inicio': (datetime.date.today() + datetime.timedelta(days=15)).isoformat(),
            'data_fim': (datetime.date.today() + datetime.timedelta(days=25)).isoformat(),
        }
        resposta = self.client.post('/api/ferias/', dados)
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_data_fim_anterior_a_inicio_e_rejeitada(self):
        dados = {
            'motorista': self.motorista.id,
            'data_inicio': (datetime.date.today() + datetime.timedelta(days=10)).isoformat(),
            'data_fim': (datetime.date.today() + datetime.timedelta(days=5)).isoformat(),
        }
        resposta = self.client.post('/api/ferias/', dados)
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
