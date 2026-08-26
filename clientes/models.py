from django.core.validators import RegexValidator
from django.db import models

# Validações simples de formato (apenas quantidade/tipo de caracteres).
# Não implementamos o cálculo dos dígitos verificadores de CPF/CNPJ:
# isso está fora do escopo deste projeto e não é exigido pela
# especificação — o objetivo aqui é validar o formato básico do dado.
validador_telefone = RegexValidator(
    regex=r'^\d{10,11}$',
    message='Informe o telefone apenas com números e DDD (10 ou 11 dígitos). Ex: 11987654321',
)

validador_cep = RegexValidator(
    regex=r'^\d{8}$',
    message='Informe o CEP apenas com números (8 dígitos). Ex: 01310100',
)


class TipoPessoa(models.TextChoices):
    FISICA = 'PF', 'Pessoa Física'
    JURIDICA = 'PJ', 'Pessoa Jurídica'


class Cliente(models.Model):
    """Cliente que solicita entregas para a transportadora."""

    tipo_pessoa = models.CharField(
        max_length=2,
        choices=TipoPessoa.choices,
        default=TipoPessoa.JURIDICA,
        verbose_name='Tipo de pessoa',
    )
    nome = models.CharField(
        max_length=150,
        verbose_name='Nome / Razão social',
    )
    cpf_cnpj = models.CharField(
        max_length=14,
        unique=True,
        verbose_name='CPF ou CNPJ',
        help_text='Somente números. 11 dígitos para CPF ou 14 para CNPJ.',
    )
    telefone = models.CharField(
        max_length=11,
        validators=[validador_telefone],
        verbose_name='Telefone',
    )
    email = models.EmailField(blank=True, verbose_name='E-mail')

    endereco = models.CharField(max_length=200, verbose_name='Endereço')
    cidade = models.CharField(max_length=100, verbose_name='Cidade')
    estado = models.CharField(max_length=2, verbose_name='UF')
    cep = models.CharField(
        max_length=8,
        validators=[validador_cep],
        verbose_name='CEP',
    )

    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name='Data de cadastro')
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name='Última atualização')

    class Meta:
        ordering = ['nome']
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return self.nome
