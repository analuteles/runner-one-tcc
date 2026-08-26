from django.contrib import admin

from .models import Motorista


@admin.register(Motorista)
class MotoristaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cpf', 'cnh_numero', 'cnh_categoria', 'cnh_validade', 'ativo']
    list_filter = ['ativo', 'cnh_categoria']
    search_fields = ['nome', 'cpf', 'cnh_numero']
