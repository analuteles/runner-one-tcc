from django.contrib import admin

from .models import Ocorrencia


@admin.register(Ocorrencia)
class OcorrenciaAdmin(admin.ModelAdmin):
    list_display = ['id', 'entrega', 'tipo', 'data']
    list_filter = ['tipo']
    search_fields = ['descricao', 'observacao']
