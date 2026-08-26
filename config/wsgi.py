"""
Configuração WSGI para o projeto Runner One.
Usada para implantar o projeto em servidores WSGI tradicionais.
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
