from django.db import models
from django.utils import timezone

from motoristas.models import Motorista


class SituacaoFerias(models.TextChoices):
    AGENDADA = 'AGENDADA', 'Agendada'
    EM_ANDAMENTO = 'EM_ANDAMENTO', 'Em andamento'
    CONCLUIDA = 'CONCLUIDA', 'Concluída'


class Ferias(models.Model):
    """Período de férias registrado para um motorista."""

    motorista = models.ForeignKey(
        Motorista,
        on_delete=models.CASCADE,
        related_name='ferias',
        verbose_name='Motorista',
    )
    data_inicio = models.DateField(verbose_name='Data de início')
    data_fim = models.DateField(verbose_name='Data de término')
    observacao = models.TextField(blank=True, verbose_name='Observação')

    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name='Data de cadastro')

    class Meta:
        ordering = ['-data_inicio']
        verbose_name = 'Férias'
        verbose_name_plural = 'Férias'

    def __str__(self):
        return f'Férias de {self.motorista.nome} ({self.data_inicio} a {self.data_fim})'

    @property
    def situacao(self):
        hoje = timezone.localdate()
        if hoje < self.data_inicio:
            return SituacaoFerias.AGENDADA
        if hoje > self.data_fim:
            return SituacaoFerias.CONCLUIDA
        return SituacaoFerias.EM_ANDAMENTO
