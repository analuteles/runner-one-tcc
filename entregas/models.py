from django.db import models
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from motoristas.models import Motorista
from pedidos.models import Pedido
from veiculos.models import SituacaoVeiculo, Veiculo


class StatusEntrega(models.TextChoices):
    AGUARDANDO = 'AGUARDANDO', 'Aguardando'
    EM_ROTA = 'EM_ROTA', 'Em rota'
    ENTREGUE = 'ENTREGUE', 'Entregue'
    ATRASADA = 'ATRASADA', 'Atrasada'
    CANCELADA = 'CANCELADA', 'Cancelada'


class EntregaQuerySet(models.QuerySet):
    def atualizar_atrasadas(self):
        """
        Marca como ATRASADA toda entrega que ainda está aguardando ou
        em rota, mas cuja data prevista já passou (regra: "uma entrega
        poderá ser identificada como ATRASADA quando não for concluída
        dentro do prazo previsto").

        É chamado sempre que a lista/detalhe de entregas é consultado
        (ver EntregaViewSet.get_queryset). Assim, o status fica correto
        sem precisar de um processo assíncrono ou agendado rodando em
        segundo plano — o que o projeto pede para evitar. Também existe
        um management command (atualizar_atrasadas) que faz a mesma
        coisa, caso o time queira agendar isso via cron no servidor.
        """
        hoje = timezone.localdate()
        return self.filter(
            status__in=[StatusEntrega.AGUARDANDO, StatusEntrega.EM_ROTA],
            data_prevista__lt=hoje,
        ).update(status=StatusEntrega.ATRASADA)


class Entrega(models.Model):
    """
    Entrega — a EXECUÇÃO de um pedido.

    Toda entrega está ligada a um pedido. Motorista e veículo só se
    tornam obrigatórios quando a entrega é iniciada (regra de negócio
    nº 2 da especificação), por isso os dois campos aceitam nulo.
    """

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.PROTECT,
        related_name='entregas',
        verbose_name='Pedido',
    )
    motorista = models.ForeignKey(
        Motorista,
        on_delete=models.PROTECT,
        related_name='entregas',
        null=True,
        blank=True,
        verbose_name='Motorista',
    )
    veiculo = models.ForeignKey(
        Veiculo,
        on_delete=models.PROTECT,
        related_name='entregas',
        null=True,
        blank=True,
        verbose_name='Veículo',
    )

    status = models.CharField(
        max_length=20,
        choices=StatusEntrega.choices,
        default=StatusEntrega.AGUARDANDO,
        verbose_name='Status',
    )

    data_prevista = models.DateField(verbose_name='Data prevista de entrega')
    hora_saida = models.DateTimeField(null=True, blank=True, verbose_name='Horário de saída')
    hora_chegada = models.DateTimeField(null=True, blank=True, verbose_name='Horário de chegada')

    motivo_cancelamento = models.TextField(blank=True, verbose_name='Motivo do cancelamento')

    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name='Data de criação')
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name='Última atualização')

    objects = EntregaQuerySet.as_manager()

    class Meta:
        ordering = ['-data_criacao']
        verbose_name = 'Entrega'
        verbose_name_plural = 'Entregas'

    def __str__(self):
        return f'Entrega #{self.id} - Pedido #{self.pedido_id} ({self.get_status_display()})'

    # ------------------------------------------------------------
    # Regras de transição de status (itens 13 a 16 da especificação)
    #
    # ATRASADA é tratado como uma "variação" tanto de AGUARDANDO
    # quanto de EM_ROTA (a entrega pode estar atrasada sem nunca ter
    # saído, ou atrasada já estando a caminho). Por isso ela também
    # pode ser iniciada, finalizada ou cancelada — o que muda é a
    # partir de qual status "base" ela está.
    #
    # Transições continuam proibidas nos casos que a especificação
    # define explicitamente:
    #   ENTREGUE  -> EM_ROTA      (não permitido)
    #   ENTREGUE  -> AGUARDANDO   (não permitido)
    #   CANCELADA -> ENTREGUE     (não permitido)
    # ------------------------------------------------------------

    def pode_iniciar(self):
        return self.status in (StatusEntrega.AGUARDANDO, StatusEntrega.ATRASADA)

    def iniciar(self):
        """Início da entrega (item 14): sai do status aguardando/atrasada para em rota."""
        if not self.pode_iniciar():
            raise ValidationError('Não é possível iniciar esta entrega.')
        if not self.motorista_id or not self.veiculo_id:
            raise ValidationError(
                'É necessário informar motorista e veículo antes de iniciar a entrega.'
            )
        if not self.motorista.ativo:
            raise ValidationError('O motorista selecionado está inativo.')
        if self.veiculo.situacao != SituacaoVeiculo.DISPONIVEL:
            raise ValidationError('O veículo selecionado está indisponível.')

        self.hora_saida = timezone.now()
        self.status = StatusEntrega.EM_ROTA
        self.save(update_fields=['hora_saida', 'status', 'data_atualizacao'])

        self.veiculo.situacao = SituacaoVeiculo.EM_USO
        self.veiculo.save(update_fields=['situacao'])

    def pode_finalizar(self):
        return self.status in (StatusEntrega.EM_ROTA, StatusEntrega.ATRASADA)

    def finalizar(self):
        """Finalização da entrega (item 15): registra chegada e conclui a entrega."""
        if not self.pode_finalizar():
            raise ValidationError('Não é possível finalizar esta entrega.')

        self.hora_chegada = timezone.now()
        self.status = StatusEntrega.ENTREGUE
        self.save(update_fields=['hora_chegada', 'status', 'data_atualizacao'])

        if self.veiculo_id and self.veiculo.situacao == SituacaoVeiculo.EM_USO:
            self.veiculo.situacao = SituacaoVeiculo.DISPONIVEL
            self.veiculo.save(update_fields=['situacao'])

    def pode_cancelar(self):
        return self.status in (
            StatusEntrega.AGUARDANDO,
            StatusEntrega.EM_ROTA,
            StatusEntrega.ATRASADA,
        )

    def cancelar(self, motivo):
        """Cancelamento da entrega (item 16). Uma entrega já ENTREGUE não pode ser cancelada."""
        if not self.pode_cancelar():
            raise ValidationError('Não é possível cancelar esta entrega.')
        if not motivo or not motivo.strip():
            raise ValidationError('É necessário informar o motivo do cancelamento.')

        self.status = StatusEntrega.CANCELADA
        self.motivo_cancelamento = motivo
        self.save(update_fields=['status', 'motivo_cancelamento', 'data_atualizacao'])

        if self.veiculo_id and self.veiculo.situacao == SituacaoVeiculo.EM_USO:
            self.veiculo.situacao = SituacaoVeiculo.DISPONIVEL
            self.veiculo.save(update_fields=['situacao'])
