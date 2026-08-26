from django.db import models
from django.utils import timezone

from entregas.models import Entrega


class TipoOcorrencia(models.TextChoices):
    ATRASO = 'ATRASO', 'Atraso'
    PROBLEMA_VEICULO = 'PROBLEMA_VEICULO', 'Problema com o veículo'
    PROBLEMA_ENTREGA = 'PROBLEMA_ENTREGA', 'Problema na entrega'
    ENDERECO_INCORRETO = 'ENDERECO_INCORRETO', 'Endereço incorreto'
    OUTROS = 'OUTROS', 'Outros'


class Ocorrencia(models.Model):
    """Registro de um problema ou evento ocorrido durante uma entrega."""

    entrega = models.ForeignKey(
        Entrega,
        on_delete=models.CASCADE,
        related_name='ocorrencias',
        verbose_name='Entrega',
    )
    tipo = models.CharField(max_length=30, choices=TipoOcorrencia.choices, verbose_name='Tipo')
    descricao = models.TextField(verbose_name='Descrição')
    data = models.DateTimeField(default=timezone.now, verbose_name='Data da ocorrência')
    observacao = models.TextField(blank=True, verbose_name='Observação')

    class Meta:
        ordering = ['-data']
        verbose_name = 'Ocorrência'
        verbose_name_plural = 'Ocorrências'

    def __str__(self):
        return f'{self.get_tipo_display()} - Entrega #{self.entrega_id}'
