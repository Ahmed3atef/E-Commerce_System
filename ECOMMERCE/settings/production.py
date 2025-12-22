from .common import *


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/
DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
# https://djecrety.ir
SECRET_KEY = os.environ.get('SECRET_KEY')

ALLOWED_HOSTS = []

DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME'),
            'HOST': os.environ.get('DB_HOST'),
            'USER': os.environ.get('DB_USER'),
            'PASSWORD': os.environ.get('DB_PASS'),
            'PORT': os.environ.get('DB_PORT')
        }
    }

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True 
EMAIL_USE_SSL = False
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')