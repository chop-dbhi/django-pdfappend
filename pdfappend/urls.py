from django.conf.urls import patterns, url
from pdfappend.resources import PDFAppender

urlpatterns =[
    url(r'^append/', PDFAppender.as_view()),
]
