from django.contrib import admin

from .models import Entrega


@admin.register(Entrega)
class EntregaAdmin(admin.ModelAdmin):
    list_display = ['id', 'pedido', 'motorista', 'veiculo', 'status', 'data_prevista']
    list_filter = ['status']
    search_fields = ['pedido__origem', 'pedido__destino', 'motorista__nome', 'veiculo__placa']
    readonly_fields = ['hora_saida', 'hora_chegada', 'data_criacao', 'data_atualizacao']
