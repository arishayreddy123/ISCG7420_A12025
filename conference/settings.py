import os
import environ
from pathlib import Path

# 1) Define BASE_DIR so we know where .env lives
BASE_DIR = Path(__file__).resolve().parent.parent

# 2) Create the Env instance (you can give DEBUG a default cast here)
env = environ.Env(
    DEBUG=(bool, False)
)

# 3) Read the .env file into environment
env.read_env(env_file=str(BASE_DIR / '.env'))

# 4) Now retrieve values from it
SECRET_KEY = env('SECRET_KEY')        # raises if missing
DEBUG      = env('DEBUG')             # already a bool

ALLOWED_HOSTS = ['.vercel.app', 'localhost']



INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'reservations.apps.ReservationsConfig',
    'widget_tweaks',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'conference.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ BASE_DIR / 'templates' ],
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

WSGI_APPLICATION = 'conference.wsgi.application'

DATABASES = {
'default': {
    'ENGINE':   'django.db.backends.postgresql_psycopg2',
    'NAME':     env('DB_NAME'),
    'USER':     env('DB_USER'),
    'PASSWORD': env('DB_PASSWORD'),
    'HOST':     env('DB_HOST'),
    'PORT':     env('DB_PORT', default='5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Pacific/Auckland'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [ BASE_DIR / 'static' ]
STATIC_ROOT = BASE_DIR / 'staticfiles'



# Email (console for dev)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Auth redirects
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'reservations:home'
LOGOUT_REDIRECT_URL = 'reservations:home'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



# Use SendGrid via SMTP
EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = 'smtp.sendgrid.net'
EMAIL_HOST_USER     = 'apikey'                     # this is literally "apikey"
EMAIL_HOST_PASSWORD = os.getenv('SENDGRID_API_KEY')  # from env or django‑environ
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True

# the “from” address for outgoing mail
DEFAULT_FROM_EMAIL  = 'arishay.r16@gmail.com'

