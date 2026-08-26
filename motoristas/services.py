"""
Funções de apoio ao módulo de motoristas.

Colocamos aqui o cálculo de desempenho para que ele possa ser usado
tanto pela rota /api/motoristas/{id}/desempenho/ quanto pelo relatório
geral em /api/relatorios/desempenho/, sem duplicar a lógica.

Importante: os indicadores são apenas contagens simples feitas em cima
das entregas já registradas. Não há inteligência artificial, machine
learning ou qualquer tipo de previsão — conforme pedido na
especificação do projeto.
"""


def calcular_desempenho(motorista):
    """Calcula os indicadores simples de desempenho de um motorista."""
    # Import feito aqui dentro (e não no topo do arquivo) apenas para
    # deixar explícito que este cálculo depende dos dados de entregas.
    from entregas.models import Entrega, StatusEntrega

    entregas_do_motorista = Entrega.objects.filter(motorista=motorista)

    total = entregas_do_motorista.count()
    concluidas = entregas_do_motorista.filter(status=StatusEntrega.ENTREGUE).count()
    atrasadas = entregas_do_motorista.filter(status=StatusEntrega.ATRASADA).count()
    canceladas = entregas_do_motorista.filter(status=StatusEntrega.CANCELADA).count()
    em_andamento = entregas_do_motorista.filter(
        status__in=[StatusEntrega.AGUARDANDO, StatusEntrega.EM_ROTA]
    ).count()

    produtividade_percentual = round((concluidas / total) * 100, 2) if total else 0.0

    return {
        'motorista_id': motorista.id,
        'motorista_nome': motorista.nome,
        'total_entregas': total,
        'entregas_concluidas': concluidas,
        'entregas_atrasadas': atrasadas,
        'entregas_canceladas': canceladas,
        'entregas_em_andamento': em_andamento,
        'produtividade_percentual': produtividade_percentual,
    }
