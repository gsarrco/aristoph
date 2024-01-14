import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = '...'

DEBUG = False

ALLOWED_HOSTS = ['...']

SENDGRID_API_KEY = '...'

RECAPTCHA_PUBLIC_KEY = '...'
RECAPTCHA_PRIVATE_KEY = '...'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '...',
        'USER': '...',
        'PASSWORD': '...',
        'HOST': 'localhost',
        'PORT': '',
    }
}

# STATIC_ROOT = "..."

ALGOLIA = {
    'APPLICATION_ID': '...',
    'API_KEY': '...',
    'SEARCH_KEY': '...'
}

TELEGRAM_TOKEN = '...'
TELEGRAM_DOMAIN = '...'

DEFAULT_FROM_EMAIL = "Aristoph <...@...>" # like this: "Aristoph <support@aristoph.ext>"
