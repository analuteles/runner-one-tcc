"""
Configuração ASGI para o projeto Runner One.
Incluída por padrão pelo Django; o projeto não usa recursos
assíncronos, mas o arquivo é mantido para compatibilidade.
"""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_asgi_application()
