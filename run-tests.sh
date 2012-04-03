#!/bin/sh
PYTHONPATH=. DJANGO_SETTINGS_MODULE='pdfappend.tests.settings' coverage run ../bin/django-admin.py test
coverage html
