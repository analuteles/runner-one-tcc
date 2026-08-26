from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    """
    Ponto de entrada da API do Runner One.

    Retorna os links para os principais módulos do sistema, para
    facilitar a exploração da API (inclusive pelo time de frontend).
    """
    dados = {
        'clientes': reverse('cliente-list', request=request, format=format),
        'motoristas': reverse('motorista-list', request=request, format=format),
        'veiculos': reverse('veiculo-list', request=request, format=format),
        'pedidos': reverse('pedido-list', request=request, format=format),
        'cargas': reverse('carga-list', request=request, format=format),
        'entregas': reverse('entrega-list', request=request, format=format),
        'ocorrencias': reverse('ocorrencia-list', request=request, format=format),
        'multas': reverse('multa-list', request=request, format=format),
        'documentos': reverse('documento-list', request=request, format=format),
        'ferias': reverse('ferias-list', request=request, format=format),
        'relatorios': {
            'entregas': reverse('relatorio-entregas', request=request, format=format),
            'desempenho': reverse('relatorio-desempenho', request=request, format=format),
            'faturamento': reverse('relatorio-faturamento', request=request, format=format),
        },
        'autenticacao': {
            'obter_token': reverse('api-token-auth', request=request, format=format),
        },
    }
    return Response(dados)
