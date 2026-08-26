from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from .models import SituacaoVeiculo, Veiculo


class VeiculoTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='senha123')
        self.client.force_authenticate(user=self.user)

    def test_criar_veiculo(self):
        dados = {
            'placa': 'abc1d23',
            'modelo': 'Sprinter',
            'marca': 'Mercedes-Benz',
            'ano': 2022,
            'capacidade_carga_kg': '1500.00',
        }
        resposta = self.client.post('/api/veiculos/', dados)
        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resposta.data['placa'], 'ABC1D23')
        self.assertTrue(resposta.data['disponivel'])

    def test_placa_invalida_e_rejeitada(self):
        dados = {
            'placa': '1234567',
            'modelo': 'Sprinter',
            'marca': 'Mercedes-Benz',
            'ano': 2022,
            'capacidade_carga_kg': '1500.00',
        }
        resposta = self.client.post('/api/veiculos/', dados)
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_excluir_veiculo_marca_como_inativo(self):
        veiculo = Veiculo.objects.create(
            placa='XYZ9A87', modelo='Daily', marca='Iveco', ano=2020, capacidade_carga_kg=2000,
        )
        resposta = self.client.delete(f'/api/veiculos/{veiculo.id}/')
        self.assertEqual(resposta.status_code, status.HTTP_204_NO_CONTENT)
        veiculo.refresh_from_db()
        self.assertEqual(veiculo.situacao, SituacaoVeiculo.INATIVO)
