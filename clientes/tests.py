from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Cliente, TipoPessoa


class ClienteTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='senha123')
        self.client.force_authenticate(user=self.user)

    def test_criar_cliente_pessoa_juridica(self):
        dados = {
            'tipo_pessoa': TipoPessoa.JURIDICA,
            'nome': 'Transportes Rápidos LTDA',
            'cpf_cnpj': '12345678000199',
            'telefone': '11999998888',
            'email': 'contato@rapidos.com',
            'endereco': 'Rua das Cargas, 100',
            'cidade': 'São Paulo',
            'estado': 'sp',
            'cep': '01310100',
        }
        resposta = self.client.post('/api/clientes/', dados)
        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resposta.data['estado'], 'SP')  # validate_estado deve colocar em maiúsculas

    def test_cnpj_com_tamanho_errado_e_rejeitado(self):
        dados = {
            'tipo_pessoa': TipoPessoa.JURIDICA,
            'nome': 'Empresa Errada',
            'cpf_cnpj': '123',
            'telefone': '11999998888',
            'endereco': 'Rua X, 1',
            'cidade': 'São Paulo',
            'estado': 'SP',
            'cep': '01310100',
        }
        resposta = self.client.post('/api/clientes/', dados)
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_listar_clientes(self):
        Cliente.objects.create(
            tipo_pessoa=TipoPessoa.FISICA, nome='João Silva', cpf_cnpj='12345678901',
            telefone='11988887777', endereco='Rua A, 1', cidade='Campinas',
            estado='SP', cep='13010000',
        )
        resposta = self.client.get('/api/clientes/')
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data['count'], 1)

    def test_excluir_cliente_apenas_inativa(self):
        cliente = Cliente.objects.create(
            tipo_pessoa=TipoPessoa.FISICA, nome='Maria Souza', cpf_cnpj='98765432100',
            telefone='11977776666', endereco='Rua B, 2', cidade='Osasco',
            estado='SP', cep='06010000',
        )
        resposta = self.client.delete(f'/api/clientes/{cliente.id}/')
        self.assertEqual(resposta.status_code, status.HTTP_204_NO_CONTENT)
        cliente.refresh_from_db()
        self.assertFalse(cliente.ativo)
        self.assertTrue(Cliente.objects.filter(id=cliente.id).exists())

    def test_acesso_sem_autenticacao_e_negado(self):
        self.client.force_authenticate(user=None)
        resposta = self.client.get('/api/clientes/')
        self.assertEqual(resposta.status_code, status.HTTP_401_UNAUTHORIZED)
