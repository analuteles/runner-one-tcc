"""
Configurações do projeto Runner One.

Projeto de TCC — Ensino Médio Técnico em Desenvolvimento de Sistemas.

Este arquivo concentra as configurações do Django e do Django REST
Framework. Por padrão o projeto usa SQLite para facilitar o
desenvolvimento e os testes de qualquer integrante da equipe sem
precisar instalar um servidor de banco de dados. A configuração para
usar PostgreSQL em produção fica pronta (comentada) mais abaixo.
"""

import os
from datetime import timedelta
from pathlib import Path

# Diretório raiz do projeto (onde fica o manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent


# ==================================================
# SEGURANÇA
# ==================================================
# Em produção, a SECRET_KEY e o DEBUG devem vir de variáveis de
# ambiente, nunca ficar fixos no código-fonte.

SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'chave-de-desenvolvimento-runner-one-trocar-em-producao',
)

DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',')


# ==================================================
# APLICAÇÕES INSTALADAS
# ==================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',  # Permite CORS (Cross-Origin Resource Sharing) para o frontend consumir a API

    # Bibliotecas de terceiros
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',

    # Aplicações do Runner One
    'clientes',
    'motoristas',
    'veiculos',
    'pedidos',
    'cargas',
    'entregas',
    'ocorrencias',
    'multas',
    'documentos',
    'ferias',
    'relatorios',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# ==================================================
# BANCO DE DADOS
# ==================================================
# Padrão: SQLite (não exige instalação de servidor de banco).
#
# O PostgreSQL faz parte da arquitetura geral do projeto, mas não é
# necessário configurá-lo nesta etapa do desenvolvimento do backend.
# Quando o time decidir usar PostgreSQL, basta instalar o pacote
# "psycopg2-binary" e trocar o dicionário abaixo por algo como:
#
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.environ.get('DB_NAME', 'runner_one'),
#         'USER': os.environ.get('DB_USER', 'runner_one'),
#         'PASSWORD': os.environ.get('DB_PASSWORD', ''),
#         'HOST': os.environ.get('DB_HOST', 'localhost'),
#         'PORT': os.environ.get('DB_PORT', '5432'),
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ==================================================
# VALIDAÇÃO DE SENHAS
# ==================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ==================================================
# INTERNACIONALIZAÇÃO
# ==================================================

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True


# ==================================================
# ARQUIVOS ESTÁTICOS
# ==================================================

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==================================================
# DJANGO REST FRAMEWORK
# ==================================================
# Autenticação simples: sessão (útil para navegar na API pelo browser
# durante o desenvolvimento) e token (para o futuro frontend consumir
# a API). Não existe login de cliente ou de motorista — apenas os
# usuários administrativos (equipe interna) autenticam.

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]
# Observação: não usamos um EXCEPTION_HANDLER customizado de propósito.
# O comportamento padrão do DRF já devolve {"detail": "mensagem"} sempre
# que uma view levanta `serializers.ValidationError("mensagem")` com uma
# string simples — que é exatamente o formato de erro pedido na
# especificação do projeto. Criar um handler customizado só adicionaria
# complexidade desnecessária.
