"""
Rotas principais do projeto Runner One.

Cada app cuida das suas próprias rotas (arquivo urls.py de cada app).
Aqui apenas conectamos tudo sob o prefixo /api/, conforme o padrão
definido na especificação do projeto.
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from .views import api_root

urlpatterns = [
    # Painel administrativo do Django (uso interno da equipe)
    path('admin/', admin.site.urls),

    # Raiz da API — lista os módulos disponíveis
    path('api/', api_root, name='api-root'),

    # Módulos do sistema
    path('api/clientes/', include('clientes.urls')),
    path('api/motoristas/', include('motoristas.urls')),
    path('api/veiculos/', include('veiculos.urls')),
    path('api/pedidos/', include('pedidos.urls')),
    path('api/cargas/', include('cargas.urls')),
    path('api/entregas/', include('entregas.urls')),
    path('api/ocorrencias/', include('ocorrencias.urls')),
    path('api/multas/', include('multas.urls')),
    path('api/documentos/', include('documentos.urls')),
    path('api/ferias/', include('ferias.urls')),
    path('api/relatorios/', include('relatorios.urls')),

    # Autenticação
    # Login/senha -> token, para o futuro frontend autenticar suas requisições.
    path('api/auth/token/', obtain_auth_token, name='api-token-auth'),
    # Login por sessão via navegador — útil durante o desenvolvimento
    # para testar a API pela "Browsable API" do DRF.
    path('api-auth/', include('rest_framework.urls')),
]
