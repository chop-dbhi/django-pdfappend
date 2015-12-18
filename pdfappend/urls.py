from django.conf.urls import patterns, url
from pdfappend.resources import PDFAppender

urlpatterns =[
    url(r'^api/', PDFAppender.as_view()),
]
