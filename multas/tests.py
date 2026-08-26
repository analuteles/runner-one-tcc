import datetime

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from motoristas.models import Motorista

from .models import Multa


class MultaTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='senha123')
        self.client.force_authenticate(user=self.user)
        self.motorista = Motorista.objects.create(
            nome='Roberto Dias', cpf='30405060708', telefone='11955556666',
            cnh_numero='40506070809', cnh_categoria='C',
            cnh_validade=datetime.date.today() + datetime.timedelta(days=200),
            data_admissao=datetime.date.today(),
        )

    def test_criar_multa(self):
        dados = {
            'motorista': self.motorista.id,
            'motivo': 'Excesso de velocidade',
            'data': datetime.date.today().isoformat(),
            'valor': '195.23',
        }
        resposta = self.client.post('/api/multas/', dados)
        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)

    def test_listar_multas_filtrando_por_motorista(self):
        Multa.objects.create(
            motorista=self.motorista, motivo='Estacionamento irregular',
            data=datetime.date.today(), valor=88.38,
        )
        resposta = self.client.get(f'/api/multas/?motorista={self.motorista.id}')
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data['count'], 1)
