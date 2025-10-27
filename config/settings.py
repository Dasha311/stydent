"""
Django settings for config project (ready for PythonAnywhere).

Примечания:
- Значения чувствительных данных (SECRET_KEY, EMAIL_PASSWORD и т.п.) берутся из
  переменных окружения, если они заданы. Это безопаснее для публичного репозитория.
- Для локальной разработки можно оставить переменные окружения не заданными,
  тогда будут использованы безопасные значения по умолчанию (DEBUG=True).
"""

import os
from pathlib import Path
from celery.schedules import crontab

# --- BASE ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- SECURITY / секреты (используем окружение, если есть) ---
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-development-placeholder-change-me"  # <- замените в продакшне
)
# DEBUG = False в продакшне (на PythonAnywhere можно временно True для отладки)
DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() in ("1", "true", "yes")

# ALLOWED_HOSTS: прочитать из окружения или задать pythonanywhere домен
DEFAULT_ALLOWED = ["127.0.0.1", "localhost", "heawer.pythonanywhere.com"]
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS")
if ALLOWED_HOSTS:
    ALLOWED_HOSTS = [h.strip() for h in ALLOWED_HOSTS.split(",") if h.strip()]
else:
    ALLOWED_HOSTS = DEFAULT_ALLOWED

# --- INSTALLED APPS ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # REST + extras
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',

    # project apps
    'accounts',
    'courses',
    'api',
    'frontend',
]

# --- MIDDLEWARE ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # отдача статики
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --- URL / templates / WSGI ---
ROOT_URLCONF = 'config.urls'  # оставляем как есть у тебя
TEMPLATES_DIR = BASE_DIR / 'frontend' / 'templates'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(TEMPLATES_DIR)],
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

# --- DATABASE (по умолчанию sqlite, удобно на PythonAnywhere) ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(BASE_DIR / 'db.sqlite3'),
    }
}

# --- PASSWORD VALIDATION ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- INTERNATIONALIZATION ---
LANGUAGE_CODE = 'ru'
LANGUAGES = [
    ('ru', 'Russian'),
    ('kk', 'Kazakh'),
    ('en', 'English'),
]
LOCALE_PATHS = [str(BASE_DIR / 'locale')]
# Установим часовой пояс по твоему таймзоне (Asia/Almaty)
TIME_ZONE = os.environ.get("DJANGO_TIME_ZONE", "Asia/Almaty")
USE_I18N = True
USE_TZ = True

# --- STATIC / MEDIA ---
STATIC_URL = '/static/'

# указываем где лежат исходники статики (если используешь frontend/static)
STATICFILES_DIRS = [str(BASE_DIR / 'frontend' / 'static')]

# куда collectstatic будет складывать готовые файлы (обязательно)
STATIC_ROOT = str(BASE_DIR / 'staticfiles')

# WhiteNoise storage (сжатие, кеширование) - требует установки whitenoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = str(BASE_DIR / 'media')

# --- AUTH / DEFAULT FIELD ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'accounts.CustomUser'

# --- REST FRAMEWORK ---
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '1000/day',
        'login': '5/minute',
        'register': '5/minute',
    },
}

# --- CORS ---
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
# если нужен production origin (пример)
if "heawer.pythonanywhere.com" not in CORS_ALLOWED_ORIGINS:
    CORS_ALLOWED_ORIGINS.append("https://heawer.pythonanywhere.com")

# --- EMAIL (используем окружение; НЕ хранить пароль в репозитории) ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True").lower() in ("1", "true", "yes")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")  # установи в окружении
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")  # установи в окружении
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
DEFAULT_DOMAIN = os.environ.get("DEFAULT_DOMAIN", "http://localhost:8000")

# --- Celery (по умолчанию локальный Redis, если доступен) ---
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

CELERY_BEAT_SCHEDULE = {
    'module-reminders': {
        'task': 'accounts.tasks.send_module_reminders',
        'schedule': crontab(hour=9, minute=0),
    },
}
