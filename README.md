# django-pdfappend
Very simple django-app providing a rest API to retrieve multiple pdfs and
append them into a single pdf.

Pass the the urls of the pdfs in the querystring to the api. A single pdf will be returned.
For example, if urlencoded, a request might look like this:

```
api/?pdfs%3Dhttp%3A%2F%2Fyourcontentsite.com%2Fpdf1.pdf%26pdfs%3Dhttp%3A%2F%2Fyourcontentsite%2Fpdf2.pdf
```
You may also use numbered pdf parameters starting at 0 (pdf0...pdfN) instead of a single pdfs argument (but not both).


This is currently setup to run as a standalone service in Docker.

To build it:

    docker build -t pdf .

To run a standalone webserver:

    docker run -d -p 8000:8000 -e SECRET_KEY=<DJANGO_SECRET_KEY> pdf /opt/app/scripts/uwsgi.sh
    
To run behind an nginx reverse proxy:

    docker run -d -e FORCE_SCRIPT_NAME=/pdfappend -e SECRET_KEY=<DJANGO_SECRET_KEY> pdf


Environment Variables

* LOGGING_ENABLED: Enable logging to the console
* ELASTICSEARCH_HOST: Enable logging to an Elasticsearch server
* ELASTICSEARCH_PORT: Override default Elasticsearch port of 9200
* ELASTICSEARCH_INDEX: Set the index to log to on Elasticsearch. Defaults to "pdfappend"
* FORCE_SCRIPT_NAME: The endpoint on the server to mount the service
