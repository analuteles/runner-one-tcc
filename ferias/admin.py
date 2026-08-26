from django.contrib import admin

from .models import Ferias


@admin.register(Ferias)
class FeriasAdmin(admin.ModelAdmin):
    list_display = ['id', 'motorista', 'data_inicio', 'data_fim']
    search_fields = ['motorista__nome']
