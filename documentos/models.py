from django.db import models
from django.utils import timezone

from motoristas.models import Motorista

DIAS_ALERTA_VENCIMENTO = 30


class TipoDocumento(models.TextChoices):
    CNH = 'CNH', 'CNH'
    ASO = 'ASO', 'Atestado de Saúde Ocupacional'
    CERTIDAO_ANTECEDENTES = 'CERTIDAO_ANTECEDENTES', 'Certidão de antecedentes'
    OUTROS = 'OUTROS', 'Outros'


class SituacaoDocumento(models.TextChoices):
    VALIDO = 'VALIDO', 'Válido'
    A_VENCER = 'A_VENCER', 'A vencer'
    VENCIDO = 'VENCIDO', 'Vencido'


class Documento(models.Model):
    """Documento cadastrado para um motorista (CNH, exames, certidões etc.)."""

    motorista = models.ForeignKey(
        Motorista,
        on_delete=models.CASCADE,
        related_name='documentos',
        verbose_name='Motorista',
    )
    tipo_documento = models.CharField(
        max_length=30,
        choices=TipoDocumento.choices,
        verbose_name='Tipo de documento',
    )
    numero = models.CharField(max_length=50, blank=True, verbose_name='Número')
    data_emissao = models.DateField(verbose_name='Data de emissão')
    data_validade = models.DateField(verbose_name='Data de validade')
    observacao = models.TextField(blank=True, verbose_name='Observação')

    class Meta:
        ordering = ['data_validade']
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'

    def __str__(self):
        return f'{self.get_tipo_documento_display()} - {self.motorista.nome}'

    @property
    def situacao(self):
        # Calculado na hora, a partir da data de validade — assim não
        # existe o risco de um campo "situação" salvo no banco ficar
        # desatualizado.
        hoje = timezone.localdate()
        dias_para_vencer = (self.data_validade - hoje).days
        if dias_para_vencer < 0:
            return SituacaoDocumento.VENCIDO
        if dias_para_vencer <= DIAS_ALERTA_VENCIMENTO:
            return SituacaoDocumento.A_VENCER
        return SituacaoDocumento.VALIDO
