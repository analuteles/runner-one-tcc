import datetime

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from motoristas.models import Motorista

from .models import Documento, SituacaoDocumento, TipoDocumento


class DocumentoTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='senha123')
        self.client.force_authenticate(user=self.user)
        self.motorista = Motorista.objects.create(
            nome='Simone Rocha', cpf='50607080910', telefone='11944445555',
            cnh_numero='60708091011', cnh_categoria='B',
            cnh_validade=datetime.date.today() + datetime.timedelta(days=200),
            data_admissao=datetime.date.today(),
        )

    def test_criar_documento(self):
        dados = {
            'motorista': self.motorista.id,
            'tipo_documento': TipoDocumento.ASO,
            'data_emissao': datetime.date.today().isoformat(),
            'data_validade': (datetime.date.today() + datetime.timedelta(days=365)).isoformat(),
        }
        resposta = self.client.post('/api/documentos/', dados)
        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resposta.data['situacao'], SituacaoDocumento.VALIDO)

    def test_situacao_documento_vencido(self):
        documento = Documento.objects.create(
            motorista=self.motorista, tipo_documento=TipoDocumento.CNH,
            data_emissao=datetime.date.today() - datetime.timedelta(days=800),
            data_validade=datetime.date.today() - datetime.timedelta(days=10),
        )
        self.assertEqual(documento.situacao, SituacaoDocumento.VENCIDO)

    def test_data_validade_anterior_a_emissao_e_rejeitada(self):
        dados = {
            'motorista': self.motorista.id,
            'tipo_documento': TipoDocumento.OUTROS,
            'data_emissao': datetime.date.today().isoformat(),
            'data_validade': (datetime.date.today() - datetime.timedelta(days=5)).isoformat(),
        }
        resposta = self.client.post('/api/documentos/', dados)
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
