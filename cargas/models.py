from django.core.validators import MinValueValidator
from django.db import models

from pedidos.models import Pedido


class Carga(models.Model):
    """
    Informações da mercadoria transportada em um pedido.

    Cada pedido possui, no máximo, uma carga associada. Não controlamos
    múltiplos itens de carga por pedido — isso deixaria o projeto mais
    complexo do que o necessário para o escopo definido. O objetivo é
    apenas registrar tipo, peso e volume da mercadoria.
    """

    pedido = models.OneToOneField(
        Pedido,
        on_delete=models.CASCADE,
        related_name='carga',
        verbose_name='Pedido',
    )
    tipo_mercadoria = models.CharField(max_length=150, verbose_name='Tipo de mercadoria')
    peso_kg = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Peso (kg)',
    )
    volume_m3 = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        validators=[MinValueValidator(0.001)],
        verbose_name='Volume (m³)',
    )
    descricao = models.TextField(blank=True, verbose_name='Descrição')

    class Meta:
        verbose_name = 'Carga'
        verbose_name_plural = 'Cargas'

    def __str__(self):
        return f'Carga do pedido #{self.pedido_id} - {self.tipo_mercadoria}'
