from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from entregas.models import Entrega, StatusEntrega
from motoristas.models import Motorista
from motoristas.services import calcular_desempenho
from pedidos.models import Pedido


def _intervalo_por_periodo(request):
    """
    Lê os parâmetros de período da query string e devolve (data_inicio, data_fim).

    Aceita:
      - ?data_inicio=AAAA-MM-DD&data_fim=AAAA-MM-DD (tem prioridade quando os dois vêm válidos)
      - ?periodo=dia | semana | mes

    Se nada for informado (ou vier em formato inválido), usa "dia" (hoje) como padrão.
    """
    hoje = timezone.localdate()

    data_inicio_str = request.query_params.get('data_inicio')
    data_fim_str = request.query_params.get('data_fim')
    if data_inicio_str and data_fim_str:
        data_inicio = parse_date(data_inicio_str)
        data_fim = parse_date(data_fim_str)
        if data_inicio and data_fim:
            return data_inicio, data_fim

    periodo = request.query_params.get('periodo', 'dia')
    if periodo == 'semana':
        inicio = hoje - timedelta(days=hoje.weekday())
        fim = inicio + timedelta(days=6)
    elif periodo == 'mes':
        inicio = hoje.replace(day=1)
        if hoje.month == 12:
            proximo_mes = hoje.replace(year=hoje.year + 1, month=1, day=1)
        else:
            proximo_mes = hoje.replace(month=hoje.month + 1, day=1)
        fim = proximo_mes - timedelta(days=1)
    else:  # 'dia' (padrão) ou qualquer valor não reconhecido
        inicio = hoje
        fim = hoje

    return inicio, fim


class RelatorioEntregasView(APIView):
    """GET /api/relatorios/entregas/ — resumo das entregas previstas em um período."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        from entregas.serializers import EntregaSerializer

        Entrega.objects.atualizar_atrasadas()

        data_inicio, data_fim = _intervalo_por_periodo(request)
        entregas_qs = Entrega.objects.select_related(
            'pedido', 'pedido__cliente', 'motorista', 'veiculo'
        ).filter(data_prevista__range=[data_inicio, data_fim])

        entregas_por_status = {
            valor: entregas_qs.filter(status=valor).count() for valor, _ in StatusEntrega.choices
        }

        return Response(
            {
                'periodo': {'data_inicio': data_inicio, 'data_fim': data_fim},
                'total_entregas': entregas_qs.count(),
                'entregas_por_status': entregas_por_status,
                'entregas': EntregaSerializer(
                    entregas_qs.order_by('data_prevista'), many=True
                ).data,
            }
        )


class RelatorioDesempenhoView(APIView):
    """GET /api/relatorios/desempenho/ — desempenho de todos os motoristas ativos."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        motoristas_qs = Motorista.objects.filter(ativo=True).order_by('nome')
        dados = [calcular_desempenho(motorista) for motorista in motoristas_qs]
        return Response({'total_motoristas': len(dados), 'motoristas': dados})


class RelatorioFaturamentoView(APIView):
    """
    GET /api/relatorios/faturamento/ — soma do valor de frete dos
    pedidos cuja entrega foi concluída dentro do período informado.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        data_inicio, data_fim = _intervalo_por_periodo(request)

        pedidos_faturados = Pedido.objects.filter(
            entregas__status=StatusEntrega.ENTREGUE,
            entregas__hora_chegada__date__range=[data_inicio, data_fim],
        ).distinct()

        total_faturado = pedidos_faturados.aggregate(total=Sum('valor_frete'))['total'] or 0

        return Response(
            {
                'periodo': {'data_inicio': data_inicio, 'data_fim': data_fim},
                'quantidade_entregas_faturadas': pedidos_faturados.count(),
                'valor_total_faturado': total_faturado,
            }
        )
