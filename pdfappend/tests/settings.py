DATABASES = {
'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': 'testdb'
    }
}

ROOT_URLCONF =  'pdfappend.urls'

INSTALLED_APPS = ('pdfappend', 'pdfappend.tests', 'restlib')

