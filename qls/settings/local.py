from .base import *

PRODUCTION = False

DEBUG = True


PRINT_EANABLED = True

TRACEBACK_OFF = False

SECRET_KEY = 'g%5c%3_wib%m&g2k+muja#1907l)(ko051r^r4^vbvqb6qmnem'

ALLOWED_HOSTS = ['127.0.0.1', 'localhost',]

INSTALLED_APPS += [
   
]


DATABASES['default'] = DATABASES['local']
DATABASES['default']['USER'] 		=	None
DATABASES['default']['PASSWORD']	=	None
DATABASES['default']['HOST']		=	None
DATABASES['default']['PORT']		=	None
DATABASES['default']['TIME_ZONE']	=	None