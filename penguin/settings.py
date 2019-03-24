"""
Django settings for penguin project.

Generated by 'django-admin startproject' using Django 1.10.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['DJANGO_SECRET']

# SECURITY WARNING: don't run with debug turned on in production!
# remove for deployment
DEBUG = False

# DEV

# ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# PROD

ALLOWED_HOSTS = ['54.215.201.137', 'thepenguinpen.com', 'newpenguin.thepenguinpen.com', 'www.thepenguinpen.com']


TEMPLATE_DEBUG = False

# loggers will log to penguin.log when debug == false
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'applogfile': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'penguin.log'),
            'maxBytes': 1024*1024*15, # 15MB
            'backupCount': 10,
        },
    },

    'loggers': {
        'django.request': {
            'handlers': ['applogfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'penguin': {
            'handlers': ['applogfile',],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

# Application definition
INSTALLED_APPS = [
    'apps.users',
    'apps.shop',
    'apps.learn',
    'apps.blog',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_summernote',
    'storages',
    'sorl.thumbnail',
    'debug_toolbar',
    'autofixture',
    'django_countries',
    'phonenumber_field',
    'adminsortable',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'penguin.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, "templates"),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'penguin.context_processors.cart_count',
                'penguin.context_processors.vacation_settings',
                'django.template.context_processors.static',
            ],
        },
    },
]

WSGI_APPLICATION = 'penguin.wsgi.application'

# DEV

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'penguin',
#         'USER': 'postgres',
#         'PASSWORD': 'somepassword',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }

# PROD

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'penguin',
        'USER': 'ubuntu',
        'PASSWORD': 'root',
        'HOST': 'localhost',
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


# Internationalization

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# DEFAULT FOR SORL THUMBNAIL
THUMB_SIZE = 200,200

#session persistance settings
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 3600
SESSION_SAVE_EVERY_REQUEST = True

CART_SESSION_ID = 'cart'

# SSL settings
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# static and media storage in s3 settings
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

# aws access for IAM user
AWS_ACCESS_KEY_ID = os.environ['PENGUIN_S3_KEY']
AWS_SECRET_ACCESS_KEY = os.environ['PENGUIN_S3_SECRET']

# S3 target bucket
AWS_STORAGE_BUCKET_NAME = os.environ['PENGUIN_S3_BUCKET']

# bucket url
AWS_S3_CUSTOM_DOMAIN = '{}.s3.amazonaws.com'.format(AWS_STORAGE_BUCKET_NAME)

# permissions
AWS_DEFAULT_ACL = 'public-read'
AWS_QUERYSTRING_AUTH = False

# DEV static

# STATIC_URL = '/static/'

# PROD static
# STATIC FILES STORAGE
STATIC_LOCATION = 'static'
STATIC_URL = 'https://{}/{}/'.format(AWS_S3_CUSTOM_DOMAIN, STATIC_LOCATION)
STATICFILES_STORAGE = 'penguin.storage_backends.StaticStorage'

# media settings should be the same for dev and prod
# MEDIA FILES STORAGE
MEDIA_LOCATION = '/media/'
MEDIA_URL = "http://{}/{}".format(AWS_S3_CUSTOM_DOMAIN, MEDIA_LOCATION)
DEFAULT_FILE_STORAGE = 'penguin.storage_backends.MediaStorage'

# CUSTOM GLOBAL VARIABLES
STRIPE_PRIVATE_KEY = os.environ['STRIPE_PRIVATE_KEY']
STRIPE_TEST_PRIVATE_KEY = os.environ['STRIPE_TEST_PRIVATE_KEY']
EASYPOST_TEST_KEY = os.environ['EASYPOST_TEST_KEY']
EASYPOST_PRODUCTION_KEY = os.environ['EASYPOST_PRODUCTION_KEY']
MAILGUN_BASE_URL = "https://api.mailgun.net/v3/mg.thepenguinpen.com/"
MAILGUN_SENDER = "Rick Propas <rickpropas@gmail.com>"
MAILGUN_PRIVATE_KEY = os.environ['MAILGUN_PRIVATE_KEY']
MAILGUN_PUBLIC_KEY = os.environ['MAILGUN_PUBLIC_KEY']
