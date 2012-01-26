from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^api/', 'pdf.api.PDFAppender'),
)
