"""
Django settings for budget_lens_backend project.

Generated by 'django-admin startproject' using Django 4.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# Configure settings based on "dev mode" or "production mode"
PRODUCTION_MODE = os.getenv("PRODUCTION_MODE") == True
DEBUG = os.getenv("DEBUG") == True

if PRODUCTION_MODE and not DEBUG:
    ALLOWED_HOSTS = [
            '127.0.0.1',
            '206.81.3.66',
            'budgetlens.tech',
            'api.budgetlens.tech'
        ]
    STATIC_ROOT = os.environ.get("RECEIPT_IMAGES_ROOT")
    RECEIPT_IMAGES_DIRS = [BASE_DIR / "receipt_images"]
elif not PRODUCTION_MODE and DEBUG:
    try:
        ALLOWED_HOSTS = [
            '127.0.0.1',
            '206.81.3.66',
            'budgetlens.tech',
            '*.budgetlens.tech'
        ]
    except Exception as e:
        ALLOWED_HOSTS = []
    SECRET_KEY = '_!l0$=nq9(ib-n1dclpoh^y1z*50jxn@_%9%(elwmspw73@qa&'
    HOST_NAME = 'http://localhost:8000'


# Application definition
# python manage.py makemigrations
# python manage.py migrate

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Our apps
    'users.apps.UsersConfig',
    'receipts.apps.ReceiptsConfig',
    'friends.apps.FriendsConfig',

    # Installed apps
    'rest_framework',
    'corsheaders',
    'rest_framework.authtoken',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'users.authentication.BearerAuthentication',
    ),
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Our middleware
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'budget_lens_backend.urls'

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

WSGI_APPLICATION = 'budget_lens_backend.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

if os.getenv("POSTGRES_USER"):
    POSTGRES_USER = os.getenv("POSTGRES_USER")
else:
    POSTGRES_USER = "postgres"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',

        'NAME': os.getenv('POSTGRES_DB'),

        'USER': os.getenv('POSTGRES_USER'),

        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),

        'HOST': os.getenv('POSTGRES_HOST'),

        'PORT': os.getenv('POSTGRES_PORT'),

    }
}

if 'test' in sys.argv or 'test\\coverage' in sys.argv:  # Covers regular testing and django-coverage
    DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql'
    DATABASES['default']['NAME'] = 'bud_local_db'
    DATABASES['default']['USER'] = 'postgres'
    DATABASES['default']['PASSWORD'] = '9876'

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

RECEIPT_IMAGES_URL = 'receipt_images/'
RECEIPT_IMAGES_ROOT = os.path.join(BASE_DIR, 'receipt_images')
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

PHONENUMBER_DEFAULT_REGION = 'CA'
