from .common import *


DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
# https://djecrety.ir
SECRET_KEY = 'django-insecure-in1jq^2c@b-tl79+8z1=sliv_4jh4vt*j7#2@p$h!)e6hu*w7u'

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

if os.environ.get('ON_Render'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'ahmed3atef$ecommerce',
            'HOST': 'ahmed3atef.mysql.pythonanywhere-services.com',
            'USER':'ahmed3atef',
            'PASSWORD':'TESTserver123',
            'PORT': 3306
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


if os.environ.get('ON_PYTHONANYWHERE'):
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


if os.environ.get('ON_Render'):
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://127.0.0.1:6379/1",
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