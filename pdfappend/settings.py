import os
import sys


def get_env_variable(var_name, default=None):
    """ Get the environment variable or return an exception"""
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s environment variable" % var_name
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