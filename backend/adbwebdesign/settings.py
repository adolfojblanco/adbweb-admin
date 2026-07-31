"""
Django settings for adbwebdesign project.
"""
from datetime import timedelta
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-6&5zxt7lu%rr&40tx0wztg*cw%luove0zf^0arrstwjx8$46)w'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

CORS_ALLOW_ALL_ORIGINS = True

# Application definition

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'corsheaders',
    'drf_yasg',
    'rest_framework',
    'rest_framework_simplejwt',
]
LOCAL_APPS = [
    'apps.accounts',
    'apps.core',
    'apps.catalogs',
    'apps.billing',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'adbwebdesign.urls'

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
            ],
        },
    },
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication', # Útil para ver Swagger logueado
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated', # Permitimos el acceso general
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
}

# --- CONFIGURACIÓN DE SWAGGER (drf-yasg) ---
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': "Ingresa tu token JWT en este formato: Bearer {tu_token_aqui}"
        }
    },
    'USE_SESSION_AUTH': False, # Desactiva el login por defecto de Django en la vista de Swagger
}

WSGI_APPLICATION = 'adbwebdesign.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'adbwebdesign-admin',
        'USER': 'adolfob',
        'PASSWORD': 'Emma2023*',
        'HOST': 'server.adbwebdesign.com',
        'PORT': '5432',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# --- ARCHIVOS ESTÁTICOS (CSS, JS, Imágenes de la plantilla) ---
STATIC_URL = '/static/'
# 1. Dónde pones TÚ los archivos (tu carpeta de diseño)
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
# 2. Dónde los juntará DJANGO (El que te está pidiendo el error)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# --- ARCHIVOS MEDIA (Subidas de usuario) ---
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

SIMPLE_JWT = {
    # 1. El token que envía Angular en cada petición (El pase rápido)
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),

    # 2. El token que se usa para renovar el Access Token sin pedir contraseña
    'REFRESH_TOKEN_LIFETIME': timedelta(days=2),
}

# Internationalization
LANGUAGE_CODE = 'es-ES'

TIME_ZONE = 'Europe/Madrid'

USE_I18N = True

USE_TZ = True

AUTH_USER_MODEL = "accounts.User"

# --- EMAIL ---
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   # EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.ionos.es')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'mail@adbwebdesign.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'Adolfo17547220*')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'mail@adbwebdesign.com')

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
