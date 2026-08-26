from django.contrib import admin

from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cpf_cnpj', 'telefone', 'cidade', 'estado', 'ativo']
    list_filter = ['ativo', 'tipo_pessoa', 'estado']
    search_fields = ['nome', 'cpf_cnpj', 'email']
