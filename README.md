# django-pdfappend
Very simple django-app providing a rest API to retrieve multiple pdfs and
append them into a single pdf.

Pass the the urls of the pdfs in the querystring to the api. A single
pdf will be returned

```
api/?pdfs%3Dhttp%3A%2F%2Fyourcontentsite.com%2Fpdf1.pdf%26pdfs%3Dhttp%3A%2F%2Fyourcontentsite%2Fpdf2.pdf
```
You may also use numbered pdf parameters starting at 0 (pdf0...pdfN) instead of a single pdfs argument (but not both).

##  Features
1. Local caching of retrieved pdfs using the django file system cache
    1. Respects Expires tags
    1. Uses If-Modified-Since or If-None-Match (Etag support)
1. Supports concurrent requests using urllib3 connection pools and the workerpool library. Configurable max_threads and max_connections_per_host
    1. Requests for pdfs across more than one server will automatically be threaded. Requests to a single server will be threaded once the number of requests rises above a configurable threshold.

## Note
1. Was going to use the Python Requests library however the async module uses gevent and this was not playing well with mod_wsgi (even in the beta version of gevent 1.0). The more common use would be to run django in gunicorn or uwsgi but that was not an option. See the sequentialsession branch for a version that uses the Requests Library. You will need gevent (and libevent).

## Test coverage
Currently at ~80% test coverage. Using dummyserver implementation from urllib3.  This allows each unittest to have it's own supporting tornado web server.

## TODO

Unittest:
1. Threading for requests from more than one servers.
1. Caching.
