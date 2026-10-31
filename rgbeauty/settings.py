"""
Configuración del proyecto RG Beauty SPA.

Una sola app: `tienda` (productos, carrito, servicios y agenda).
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# En un proyecto real estas claves van en variables de entorno (Clase 8).
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'clave-solo-para-desarrollo-cambiar')
DEBUG = os.environ.get('DJANGO_DEBUG', '1') == '1'
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',   # el carrito vive en la sesión
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tienda',                    # <- única app del proyecto
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'rgbeauty.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'tienda.context_processors.carrito',   # contador del carrito en el menú
            ],
        },
    },
]

WSGI_APPLICATION = 'rgbeauty.wsgi.application'

# --- Base de datos (Clase 8) -------------------------------------------------
# Antes: CREATE DATABASE rgbeauty_db CHARACTER SET utf8mb4;
DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'rgbeauty_db',
            'USER': 'root',
            'PASSWORD': '123456',
            'HOST': 'localhost',
            'PORT': '3306',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True
USE_THOUSAND_SEPARATOR = True   # $12.990 en vez de $12990

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Cuentas de usuario ---
LOGIN_URL = 'tienda:login'                # a dónde manda @login_required
LOGIN_REDIRECT_URL = 'tienda:inicio'      # después de iniciar sesión
LOGOUT_REDIRECT_URL = 'tienda:inicio'     # después de cerrar sesión
