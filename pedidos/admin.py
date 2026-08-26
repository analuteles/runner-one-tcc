from django.contrib import admin

from .models import Pedido


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'origem', 'destino', 'data_entrega_prevista', 'status']
    list_filter = ['tipo_carga']
    search_fields = ['origem', 'destino', 'cliente__nome']

    @admin.display(description='Status')
    def status(self, obj):
        return obj.status
