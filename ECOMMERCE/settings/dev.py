from .common import *


DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# SECURITY WARNING: keep the secret key used in production secret!
# https://djecrety.ir
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-in1jq^2c@b-tl79+8z1=sliv_4jh4vt*j7#2@p$h!)e6hu*w7u')


if os.environ.get('TEST_HOSTING_SERVER'):
    ALLOWED_HOSTS = [".koyeb.app", "localhost", "127.0.0.1"]
    CSRF_TRUSTED_ORIGINS = ["https://*.koyeb.app"]
else:
    ALLOWED_HOSTS = ["*"]

INTERNAL_IPS = [
    "127.0.0.1",
]


INSTALLED_APPS.extend([
    'debug_toolbar',
    'drf_spectacular',
    ])


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

if os.environ.get('TEST_HOSTING_SERVER'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'koyebdb',
            'USER': 'eco_admin',
            'PASSWORD': 'npg_newPhpj7LD9Y',
            'HOST': 'ep-sweet-heart-ag7q7eki.c-2.eu-central-1.pg.koyeb.app',
            'OPTIONS': {'sslmode': 'require'},
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'ecommerce',
            'HOST': 'localhost',
            'USER':'postgres',
            'PASSWORD':'psql',
            'PORT': 5432
        }
    }
    

SPECTACULAR_SETTINGS = {
    'TITLE': 'E-Commerce System API',
    'DESCRIPTION': 'API documentation for the E-Commerce System',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SERVE_PERMISSIONS': ['rest_framework.permissions.AllowAny'],
}


if os.environ.get('TEST_HOSTING_SERVER'):
    # EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_HOST_USER =  os.environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True 
    EMAIL_USE_SSL = False
    DEFAULT_FROM_EMAIL = 'no-reply@ecommerce-system.com'

else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 2525
    EMAIL_HOST_USER = ''
    EMAIL_HOST_PASSWORD = ''


if os.environ.get('TEST_HOSTING_SERVER'):
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "rediss://default_ro:AssCAAIgcDF0hBzPil9Kh2Ym95R2mFI0-1R0lBC2tll6dG37mzJ9zA@handy-marlin-51970.upstash.io:6379",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://127.0.0.1:6379/1",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }