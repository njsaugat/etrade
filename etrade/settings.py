from pathlib import Path

from decouple import Csv,config
BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = config("SECRET_KEY")


DEBUG = True

ALLOWED_HOSTS = []



INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    "django.contrib.sites",
    "rest_framework",
    "rest_framework.authtoken",
    "dj_rest_auth",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "dj_rest_auth.registration",
    "phonenumber_field",
    "corsheaders",
    "drf_spectacular",
    "rest_framework_simplejwt",
    #local apps
    "users",
    # "products",
    # "orders",
    # "payment"
]

MIDDLEWARE = [

    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "django.middleware.cache.UpdateCacheMiddleware",
    'django.middleware.common.CommonMiddleware',
    "django.middleware.cache.FetchFromCacheMiddleware",
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'etrade.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'etrade.wsgi.application'



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_USER_MODEL = 'users.User'

REST_AUTH_SERIALIZERS = {
    'USER_DETAILS_SERIALIZER': 'users.serializers.UserSerializer',
}


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



LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True



STATIC_URL = 'static/'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ORIGIN_ALLOW_ALL=True

AUTHENTICATION_BACKENDS=[
    "users.backends.phone_backend.PhoneNumberAuthBackend",
    "users.backends.email_backend.EmailAuthBackend",
]

REST_FRAMEWORK={
    "DEFAULT_AUTHENTICATION_CLASSES":(
        "dj_rest_auth.jwt_auth.JWTCookieAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS":"drf_spectacular.openapi.AutoSchema",
}

SITE_ID=1

REST_USE_JWT=True

JWT_AUTH_COOKIE="phonenumber-auth"
JWT_AUTH_REFRESH_COOKIE="phonenumber-refresh-token"

# ACCOUNT_EMAIL_REQUIRED=True
# ACCOUNT_UNIQUE_EMAIL=True
# ACCOUNT_USERNAME_REQUIRED=False
# ACCOUNT_EMAIL_VERIFICATION="mandatory"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD= 'email'
ACCOUNT_EMAIL_VERIFICATION = 'optional' 


EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST='smtp.gmail.com'
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=config('EMAIL_USER')
EMAIL_HOST_PASSWORD=config('EMAIL_PASS')
EMAIL_HOST_FROM=config('EMAIL_FROM')

PHONENUMBER_DEFAULT_REGION="ET"

TOKEN_LENGTH=6

TOKEN_EXPIRE_MINUTES=6


TWILIO_ACCOUNT_SID=config("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN=config("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER=config("TWILIO_PHONE_NUMBER")


# STRIPE_PUBLISHABLE_KEY=config("STRIPE_PUBLISHABLE_KEY")
# STRIPE_SECRET_KEY=config("STRIPE_SECRET_KEY")
# STRIPE_WEBHOOK_SECRET=config("STRIPE_WEBHOOK_SECRET")

# BACKEND_DOMAIN=config("BACKEND_DOMAIN")
# FRONTEND_DOMAIN=config("FRONTEND_DOMAIN")

# PAYMENT_SUCCESS_URL=config("PAYMENT_SUCCESS_URL")
# PAYMENT_CANCEL_URL=config("PAYMENT_CANCEL_URL")

# CELERY_BROKER_URL=config("CELERY_BROKER_URL")
# CELERY_RESULT_BACKEND=config("CELERY_RESULT_BACKEND")


SPECTACULAR_SETTINGS={
    "TITLE":"Etrade API",
    "DESCRIPTION":"An etrade API built using Django Rest Framework",
    "version":"1.0.0",
    "SERVE_INCLUDE_SCHEMA":False
}


CACHES={
    "default":{
        "BACKEND":"django.core.cache.backends.redis.RedisCache",
        "LOCATION":config("REDIS_BACKEND")
    }
}

CACHE_MIDDLEWARE_ALIAS="default"
CACHE_MIDDLEWARE_SECONDS=3600
CACHE_MIDDLEWARE_KEY_PREFIX=""