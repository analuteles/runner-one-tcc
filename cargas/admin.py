from django.contrib import admin

from .models import Carga


@admin.register(Carga)
class CargaAdmin(admin.ModelAdmin):
    list_display = ['id', 'pedido', 'tipo_mercadoria', 'peso_kg', 'volume_m3']
    search_fields = ['tipo_mercadoria']
