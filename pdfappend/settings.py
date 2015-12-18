import os
import sys


def get_env_variable(var_name, default=None):
    """ Get the environment variable or return an exception"""
    try:
        return os.environ[var_name]
    except KeyError:
        return default

SECRET_KEY = get_env_variable("SECRET_KEY", "REPLACE_WITH_REAL_SECRET_KEY")


DEBUG = bool(get_env_variable('DJANGO_DEBUG', False))
INSTALLED_APPS = ('pdfappend',)

FORCE_SCRIPT_NAME = get_env_variable('FORCE_SCRIPT_NAME', '')

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

ROOT_URLCONF = 'pdfappend.urls'

# Logging
# https://docs.djangoproject.com/en/1.8/topics/logging/#django-s-logging-extensions
# https://docs.djangoproject.com/en/1.8/topics/logging/#default-logging-configuration
# http://stackoverflow.com/questions/238081/how-do-you-log-server-errors-on-django-sites
if bool(get_env_variable('LOGGING_ENABLED', 0)):
    LOGGING = {
        'version': 1,
        'root': {
            'level': 'WARNING',
            'handlers': ['console'],
        },
        'disable_existing_loggers': False, 
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            },
        },
        'loggers': {
             'pdfappend': {
                'level': 'INFO',
                'handlers': ['console'],
                'propagate':False,
             },
        },
    }
    # Enable elasticsearch logging if host is provided
    if len(get_env_variable('ELASTICSEARCH_HOST', '')):
        LOGGING['handlers']['es'] = {
            'level':'INFO',
            'index':get_env_variable('ELASTICSEARCH_INDEX', 'pdfappend'),
            'class':'pdfappend.handlers.ESHandler',
            'host':get_env_variable('ELASTICSEARCH_HOST', ""),
            'port':int(get_env_variable('ELASTICSEARCH_PORT', 9200),
            'formatter': 'verbose'
        }
        LOGGING['loggers']['pdfappend']['handers'].append('es')
        