import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))
SECRET_KEY = 'django-insecure-htu0#5l42cj1%czt1b93t%bi%m^q2q39kk#m@kjm5mls435pvx'
DEBUG = True
ALLOWED_HOSTS = ['*']
LOGIN_URL = '/admin/login/'
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'task_app.apps.TaskAppConfig',
    'rest_framework',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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
ROOT_URLCONF = 'task_app.urls'
WSGI_APPLICATION = 'task_service.wsgi.application'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_URL = os.getenv('AUTH_SERVICE_URL')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'task_service.authentication.Authentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'task_service.permissions.IsAuthenticated',
    ),
}

KAFKA_SERVERS = os.getenv('KAFKA_SERVERS')
KAFKA_GROUP = os.getenv('KAFKA_GROUP')
KAFKA_CONSUMER_CONFIG = {
    'bootstrap.servers': KAFKA_SERVERS,
    'group.id': KAFKA_GROUP
}

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
