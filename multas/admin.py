from django.contrib import admin

from .models import Multa


@admin.register(Multa)
class MultaAdmin(admin.ModelAdmin):
    list_display = ['id', 'motorista', 'veiculo', 'motivo', 'data', 'valor']
    list_filter = ['data']
    search_fields = ['motivo', 'motorista__nome']
