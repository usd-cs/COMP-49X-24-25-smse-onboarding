"""
Django settings for smse_onboarding project.

Generated by 'django-admin startproject' using Django 5.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-i)^nvymxnl@fn$+1k!37@w#2+ho3#2lpvokfw(xt&vpbjyw$gu'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'smse-onboarding.dedyn.io:8080',
    'smse-onboarding.dedyn.io:8000',
    'smse-onboarding.dedyn.io',
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social_django',
    'tasks.apps.TasksConfig',
    'documents.apps.DocumentsConfig',
    'users.apps.UsersConfig',
    'dashboard.apps.DashboardConfig',
    'smse_onboarding',
    'reminders',
]

AUTHENTICATION_BACKENDS = [
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
]

ROOT_URLCONF = 'smse_onboarding.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,  # helps templates find in app directories
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
            ],
        },
    },
]

CSRF_TRUSTED_ORIGINS = [
    'https://smse-onboarding.dedyn.io:8080',
    'http://smse-onboarding.dedyn.io:8000',
    'http://smse-onboarding.dedyn.io',
    'http://localhost:8000',
]

CSRF_COOKIE_DOMAIN = [None, 'smse-onboarding.dedyn.io']

WSGI_APPLICATION = 'smse_onboarding.wsgi.application'

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY='757103126544-eo45sod0pu6hg2iiqlnvs3kp6o20kikd.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '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'
SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI = 'https://smse-onboarding.dedyn.io:8080/social-auth/complete/google-oauth2/'

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    # Enable these two lines to associate users by email
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

# Add this setting to enable email association
SOCIAL_AUTH_GOOGLE_OAUTH2_USE_UNIQUE_USER_ID = False
SOCIAL_AUTH_GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS = {
    'prompt': 'select_account'
}

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'smse-db',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
#STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    BASE_DIR / 'dashboard' / 'static',
]

FIXTURE_DIRS = [
    BASE_DIR / 'fixtures',
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/home/'
LOGOUT_REDIRECT_URL = '/users/login/'
LOGIN_URL = '/users/login/'

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Settings for file uploads
ALLOWED_DOCUMENT_TYPES = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
]
MAX_UPLOAD_SIZE = 5242880  # 5MB
