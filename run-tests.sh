#!/bin/sh
PYTHONPATH=. DJANGO_SETTINGS_MODULE='pdfappend.tests.settings' django-admin.py test