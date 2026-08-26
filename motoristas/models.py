from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

validador_cpf = RegexValidator(
    regex=r'^\d{11}$',
    message='Informe o CPF apenas com números (11 dígitos).',
)
validador_telefone = RegexValidator(
    regex=r'^\d{10,11}$',
    message='Informe o telefone apenas com números e DDD (10 ou 11 dígitos).',
)


class CategoriaCNH(models.TextChoices):
    A = 'A', 'A'
    B = 'B', 'B'
    AB = 'AB', 'AB'
    C = 'C', 'C'
    D = 'D', 'D'
    E = 'E', 'E'


class Motorista(models.Model):
    """Motorista da transportadora, responsável por realizar as entregas."""

    nome = models.CharField(max_length=150, verbose_name='Nome completo')
    cpf = models.CharField(
        max_length=11,
        unique=True,
        validators=[validador_cpf],
        verbose_name='CPF',
    )
    telefone = models.CharField(
        max_length=11,
        validators=[validador_telefone],
        verbose_name='Telefone',
    )
    email = models.EmailField(blank=True, verbose_name='E-mail')

    cnh_numero = models.CharField(max_length=11, unique=True, verbose_name='Número da CNH')
    cnh_categoria = models.CharField(
        max_length=2,
        choices=CategoriaCNH.choices,
        verbose_name='Categoria da CNH',
    )
    cnh_validade = models.DateField(verbose_name='Validade da CNH')

    data_admissao = models.DateField(verbose_name='Data de admissão')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')

    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name='Data de cadastro')
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name='Última atualização')

    class Meta:
        ordering = ['nome']
        verbose_name = 'Motorista'
        verbose_name_plural = 'Motoristas'

    def __str__(self):
        return self.nome

    @property
    def cnh_vencida(self):
        return self.cnh_validade < timezone.localdate()
