from django.core.validators import MinValueValidator
from django.db import models

from motoristas.models import Motorista
from veiculos.models import Veiculo


class Multa(models.Model):
    """Registro de multa de trânsito associada a um motorista (e, opcionalmente, a um veículo)."""

    motorista = models.ForeignKey(
        Motorista,
        on_delete=models.PROTECT,
        related_name='multas',
        verbose_name='Motorista',
    )
    veiculo = models.ForeignKey(
        Veiculo,
        on_delete=models.PROTECT,
        related_name='multas',
        null=True,
        blank=True,
        verbose_name='Veículo',
    )
    motivo = models.CharField(max_length=200, verbose_name='Motivo')
    data = models.DateField(verbose_name='Data da multa')
    valor = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Valor',
    )
    observacao = models.TextField(blank=True, verbose_name='Observação')

    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name='Data de cadastro')

    class Meta:
        ordering = ['-data']
        verbose_name = 'Multa'
        verbose_name_plural = 'Multas'

    def __str__(self):
        return f'Multa de {self.motorista.nome} em {self.data}'
