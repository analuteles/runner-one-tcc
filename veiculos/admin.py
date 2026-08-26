from django.contrib import admin

from .models import Veiculo


@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = ['placa', 'marca', 'modelo', 'ano', 'situacao']
    list_filter = ['situacao', 'marca']
    search_fields = ['placa', 'modelo', 'marca']
