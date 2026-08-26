from django.urls import path

from .views import RelatorioDesempenhoView, RelatorioEntregasView, RelatorioFaturamentoView

urlpatterns = [
    path('entregas/', RelatorioEntregasView.as_view(), name='relatorio-entregas'),
    path('desempenho/', RelatorioDesempenhoView.as_view(), name='relatorio-desempenho'),
    path('faturamento/', RelatorioFaturamentoView.as_view(), name='relatorio-faturamento'),
]
