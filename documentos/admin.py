from django.contrib import admin

from .models import Documento


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ['id', 'motorista', 'tipo_documento', 'data_validade']
    list_filter = ['tipo_documento']
    search_fields = ['motorista__nome', 'numero']
