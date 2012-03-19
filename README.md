# django-pdfappend
Very simple django-app providing a rest API to retrieve multiple pdfs and
append them into a single pdf.

Pass the the urls of the pdfs in the querystring to the api. A single
pdf will be returned

```
api/?pdfs%3Dhttp%3A%2F%2Fyourcontentsite.com%2Fpdf1.pdf%26pdfs%3Dhttp%3A%2F%2Fyourcontentsite%2Fpdf2.pdf
```

You may also use numbered parameters (starting at 0) instead of a single pdfs argument (but not both).

##  Features
1. Local caching of retrieved pdfs using the django file system cache
    1. Respects Expires tags
    1. Uses If-modified-since or If-none-match (Etag support)
1. Supports concurrent requests using urllib3 connections pools and
   the workerpool module. Configurable max_threads and max_connections_per_host
    1. Requests for pdfs across more than one server will automatically be threaded. Requests to a single server will be threaded once the number of requests rises above a configurable threshold.

## Note
1. While using numbered parameters, going past 9 parameters will break the pdf order in the final pdf.
1. Was going to use the Python Requests library however the async module uses gevent and this was not playing well with mod_wsgi (even in the beta version of gevent 1.0). The more common use would be to run django in gunicorn or uwsgi but that was not an option. See the sequentialsession branch for a version that uses the Requests Library. You will need gevent (and libevent).
