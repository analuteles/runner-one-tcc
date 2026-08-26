from django.db import models

from clientes.models import Cliente


class TipoCarga(models.TextChoices):
    GERAL = 'GERAL', 'Carga geral'
    FRAGIL = 'FRAGIL', 'Frágil'
    PERECIVEL = 'PERECIVEL', 'Perecível'
    PERIGOSA = 'PERIGOSA', 'Perigosa'
    REFRIGERADA = 'REFRIGERADA', 'Refrigerada'


class StatusPedido(models.TextChoices):
    ABERTO = 'ABERTO', 'Aberto'
    EM_ANDAMENTO = 'EM_ANDAMENTO', 'Em andamento'
    CONCLUIDO = 'CONCLUIDO', 'Concluído'
    CANCELADO = 'CANCELADO', 'Cancelado'


class Pedido(models.Model):
    """
    Pedido de entrega — a SOLICITAÇÃO feita pelo cliente.

    O pedido é diferente da entrega: o pedido é o que o cliente pede;
    a entrega é a execução desse pedido (ver app "entregas"). Um
    mesmo pedido pode ter mais de uma entrega ao longo do tempo — por
    exemplo, se a primeira entrega for cancelada e uma nova entrega
    for aberta depois para atender o mesmo pedido.
    """

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='pedidos',
        verbose_name='Cliente',
    )
    origem = models.CharField(max_length=200, verbose_name='Origem')
    destino = models.CharField(max_length=200, verbose_name='Destino')
    tipo_carga = models.CharField(
        max_length=20,
        choices=TipoCarga.choices,
        default=TipoCarga.GERAL,
        verbose_name='Tipo de carga',
    )
    data_pedido = models.DateTimeField(auto_now_add=True, verbose_name='Data do pedido')
    data_entrega_prevista = models.DateField(verbose_name='Data prevista de entrega')

    # Campo adicionado além da lista original da especificação: sem um
    # valor associado ao pedido não é possível gerar o relatório de
    # faturamento pedido no item 24. Fica opcional para não obrigar o
    # preenchimento em pedidos onde o valor ainda não foi definido.
    valor_frete = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Valor do frete',
        help_text='Usado no relatório de faturamento. Pode ficar em branco.',
    )

    observacoes = models.TextField(blank=True, verbose_name='Observações')

    class Meta:
        ordering = ['-data_pedido']
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return f'Pedido #{self.id} - {self.cliente.nome}'

    @property
    def entrega_atual(self):
        """Entrega mais recente relacionada a este pedido, se existir."""
        return self.entregas.order_by('-id').first()

    @property
    def status(self):
        """
        Status do pedido, derivado da entrega mais recente relacionada
        a ele. O pedido não guarda um status próprio no banco — isso
        evita ter a mesma informação duplicada (e possivelmente
        divergente) em dois lugares diferentes.
        """
        entrega = self.entrega_atual
        if entrega is None:
            return StatusPedido.ABERTO

        from entregas.models import StatusEntrega  # import local: evita import circular

        mapa = {
            StatusEntrega.AGUARDANDO: StatusPedido.EM_ANDAMENTO,
            StatusEntrega.EM_ROTA: StatusPedido.EM_ANDAMENTO,
            StatusEntrega.ATRASADA: StatusPedido.EM_ANDAMENTO,
            StatusEntrega.ENTREGUE: StatusPedido.CONCLUIDO,
            StatusEntrega.CANCELADA: StatusPedido.CANCELADO,
        }
        return mapa.get(entrega.status, StatusPedido.ABERTO)
