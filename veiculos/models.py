from django.core.validators import RegexValidator
from django.db import models

# Aceita tanto o formato antigo (ABC1234) quanto o padrão Mercosul (ABC1D23).
validador_placa = RegexValidator(
    regex=r'^[A-Z]{3}\d[A-Z0-9]\d{2}$',
    message='Informe a placa no formato ABC1234 ou ABC1D23 (padrão Mercosul).',
)


class SituacaoVeiculo(models.TextChoices):
    DISPONIVEL = 'DISPONIVEL', 'Disponível'
    EM_USO = 'EM_USO', 'Em uso'
    MANUTENCAO = 'MANUTENCAO', 'Em manutenção'
    INATIVO = 'INATIVO', 'Inativo'


class Veiculo(models.Model):
    """Veículo da frota usado para realizar as entregas."""

    placa = models.CharField(
        max_length=7,
        unique=True,
        validators=[validador_placa],
        verbose_name='Placa',
    )
    modelo = models.CharField(max_length=100, verbose_name='Modelo')
    marca = models.CharField(max_length=100, verbose_name='Marca')
    ano = models.PositiveIntegerField(verbose_name='Ano')
    capacidade_carga_kg = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name='Capacidade de carga (kg)',
    )
    situacao = models.CharField(
        max_length=20,
        choices=SituacaoVeiculo.choices,
        default=SituacaoVeiculo.DISPONIVEL,
        verbose_name='Situação',
    )

    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name='Data de cadastro')
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name='Última atualização')

    class Meta:
        ordering = ['placa']
        verbose_name = 'Veículo'
        verbose_name_plural = 'Veículos'

    def __str__(self):
        return f'{self.placa} - {self.marca} {self.modelo}'

    def save(self, *args, **kwargs):
        self.placa = self.placa.upper().replace('-', '').replace(' ', '')
        super().save(*args, **kwargs)

    @property
    def disponivel(self):
        return self.situacao == SituacaoVeiculo.DISPONIVEL
