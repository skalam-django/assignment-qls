from .base import *
from decouple import config


PRODUCTION = True

DEBUG = False

PRINT_EANABLED = False

TRACEBACK_OFF = False if (config('qls_TRACEBACK_OFF') is not None and config('qls_TRACEBACK_OFF')=='False') else True

SECRET_KEY = config('qls_SECRET_KEY') #g%5c%3_wib%m&g2k+muja#1907l)(ko051r^r4^vbvqb6qmnem


ALLOWED_HOSTS = [
                    
                ]

INSTALLED_APPS += [
    
]

INSTALLED_APPS += [
    'letsencrypt',
]



SSL = True if os.environ.get('qls_SSL') is not None and os.environ.get('qls_SSL')=='True' else False    
if SSL == True:
    SECURE_SSL_REDIRECT             =   True
    SECURE_PROXY_SSL_HEADER         =   ('HTTP_X_FORWARDED_PROTO', 'https')
    CSRF_COOKIE_SECURE              =   True
    SECURE_HSTS_SECONDS             =   100000
    SECURE_HSTS_INCLUDE_SUBDOMAINS  =   True
    SECURE_HSTS_PRELOAD             =   True
    SECURE_REDIRECT_EXEMPT          =   ["^insecure/"]

DATABASES['default'] = {
                        'ENGINE'    :   'django.db.backends.postgresql_psycopg2',
                        'NAME'      :   config('qls_NAME'), 
                        'USER'      :   config('qls_USER'),
                        'PASSWORD'  :   config('qls_PASSWORD'),
                        'HOST'      :   config('qls_HOST'),
                        'PORT'      :   config('qls_PORT'),
                        'TIME_ZONE' :   None,

                    }



STATIC_ROOT = os.path.join(BASE_DIR, "../static/")
MEDIA_ROOT = os.path.join(BASE_DIR, '../media/')


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {'format': '%(asctime)s  [%(levelname)s] %(name)s: %(message)s '},
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'debug.log',
            'maxBytes': 1024 * 1024 * 50,
            'backupCount': 5,
            'formatter': 'standard',
        },
        'request_handler': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'django_request.log',
            'maxBytes': 1024 * 1024 * 50,
            'backupCount': 5,
            'formatter': 'standard',
        },
    },
    'loggers': {

        '': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['request_handler'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
