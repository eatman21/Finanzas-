"""
Base Django settings for finansas project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv(
    'SECRET_KEY', 'django-insecure-your-secret-key-here-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party apps
    'crispy_forms',
    'crispy_bootstrap5',
    'django_extensions',
    'corsheaders',
    'rest_framework',
    'django_filters',
    'djmoney',

    # Local apps
    'finanzas.apps.FinanzasConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'finansas.urls'

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
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'finansas.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = []
if (BASE_DIR / 'static').exists():
    STATICFILES_DIRS.append(BASE_DIR / 'static')

if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
else:
    STATICFILES_STORAGE = 'whitenoise.storage.StaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# Session configuration
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True

# Crispy forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Email configuration
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.getenv('EMAIL_HOST')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
    DEFAULT_FROM_EMAIL = os.getenv(
        'DEFAULT_FROM_EMAIL', 'noreply@finansas.com')

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django_errors.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'finanzas': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache' if not DEBUG else 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1') if not DEBUG else '',
    }
}

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

CORS_ALLOW_CREDENTIALS = True

# Django Money settings
CURRENCIES = (
    # Major World Currencies
    'USD',   # US Dollar
    'EUR',   # Euro
    'GBP',   # British Pound
    'JPY',   # Japanese Yen
    'CHF',   # Swiss Franc
    'CAD',   # Canadian Dollar
    'AUD',   # Australian Dollar
    'NZD',   # New Zealand Dollar

    # Latin American Currencies
    'MXN',   # Mexican Peso
    'COP',   # Colombian Peso
    'ARS',   # Argentine Peso
    'BRL',   # Brazilian Real
    'CLP',   # Chilean Peso
    'PEN',   # Peruvian Sol
    'UYU',   # Uruguayan Peso
    'PYG',   # Paraguayan Guaraní
    'BOB',   # Bolivian Boliviano
    'GTQ',   # Guatemalan Quetzal
    'HNL',   # Honduran Lempira
    'NIO',   # Nicaraguan Córdoba
    'CRC',   # Costa Rican Colón
    'PAB',   # Panamanian Balboa
    'DOP',   # Dominican Peso
    'JMD',   # Jamaican Dollar
    'TTD',   # Trinidad and Tobago Dollar
    'BBD',   # Barbadian Dollar
    'XCD',   # East Caribbean Dollar
    'ANG',   # Netherlands Antillean Guilder
    'AWG',   # Aruban Florin
    'BZD',   # Belize Dollar

    # Asian Currencies
    'SGD',   # Singapore Dollar
    'HKD',   # Hong Kong Dollar
    'KRW',   # South Korean Won
    'CNY',   # Chinese Yuan
    'INR',   # Indian Rupee
    'THB',   # Thai Baht
    'VND',   # Vietnamese Dong
    'PHP',   # Philippine Peso
    'IDR',   # Indonesian Rupiah
    'MYR',   # Malaysian Ringgit
    'KHR',   # Cambodian Riel
    'LAK',   # Lao Kip
    'MMK',   # Myanmar Kyat
    'NPR',   # Nepalese Rupee
    'BDT',   # Bangladeshi Taka
    'PKR',   # Pakistani Rupee
    'LKR',   # Sri Lankan Rupee
    'MVR',   # Maldivian Rufiyaa
    'SCR',   # Seychellois Rupee
    'MUR',   # Mauritian Rupee
    'MNT',   # Mongolian Tugrik
    'KZT',   # Kazakhstani Tenge
    'UZS',   # Uzbekistani Som
    'TJS',   # Tajikistani Somoni
    'KGS',   # Kyrgyzstani Som
    'TMT',   # Turkmenistani Manat
    'AZN',   # Azerbaijani Manat
    'GEL',   # Georgian Lari
    'AMD',   # Armenian Dram
    'BYN',   # Belarusian Ruble
    'MDL',   # Moldovan Leu
    'ALL',   # Albanian Lek
    'MKD',   # Macedonian Denar

    # European Currencies
    'SEK',   # Swedish Krona
    'NOK',   # Norwegian Krone
    'DKK',   # Danish Krone
    'PLN',   # Polish Złoty
    'CZK',   # Czech Koruna
    'HUF',   # Hungarian Forint
    'RON',   # Romanian Leu
    'BGN',   # Bulgarian Lev
    'HRK',   # Croatian Kuna
    'RSD',   # Serbian Dinar
    'UAH',   # Ukrainian Hryvnia
    'ILS',   # Israeli Shekel

    # Middle Eastern & African Currencies
    'AED',   # UAE Dirham
    'SAR',   # Saudi Riyal
    'QAR',   # Qatari Riyal
    'KWD',   # Kuwaiti Dinar
    'BHD',   # Bahraini Dinar
    'OMR',   # Omani Rial
    'JOD',   # Jordanian Dinar
    'LBP',   # Lebanese Pound
    'EGP',   # Egyptian Pound
    'MAD',   # Moroccan Dirham
    'TND',   # Tunisian Dirham
    'NGN',   # Nigerian Naira
    'GHS',   # Ghanaian Cedi
    'KES',   # Kenyan Shilling
    'UGX',   # Ugandan Shilling
    'TZS',   # Tanzanian Shilling
    'ZMW',   # Zambian Kwacha
    'BWP',   # Botswana Pula
    'NAD',   # Namibian Dollar
    'ZAR',   # South African Rand
    'XOF',   # West African CFA Franc
    'XAF',   # Central African CFA Franc
    'XPF',   # CFP Franc

    # Pacific Currencies
    'FJD',   # Fijian Dollar
    'WST',   # Samoan Tala
    'TOP',   # Tongan Paʻanga
    'VUV',   # Vanuatu Vatu
    'SBD',   # Solomon Islands Dollar
    'PGK',   # Papua New Guinean Kina

    # Other Major Currencies
    'RUB',   # Russian Ruble
    'TRY',   # Turkish Lira

    # Precious Metals
    'XAU',   # Gold (troy ounce)
    'XAG',   # Silver (troy ounce)
    'XPT',   # Platinum (troy ounce)
    'XPD',   # Palladium (troy ounce)
)
DEFAULT_CURRENCY = 'MXN'
