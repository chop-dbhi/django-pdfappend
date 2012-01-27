# django-pdfappend
Very simple django-app providing a rest API to retrieve multiple pdfs and
append them into a single pdf.

Pass the the urls of the pdfs in the querystring to the api. A single
pdf will be returned

```
api/?pdfs%3Dhttp%3A%2F%2Fyourcontentsite.com%2Fpdf1.pdf%26pdfs%3Dhttp%3A%2F%2Fyourcontentsite%2Fpdf2.pdf
```
## TODO
1. Local caching of retrieved pdfs.
1. Check remote server for updates before using cached pdf.

## Note
The dependencies are properly documented in the requirements.pip and setup.py, but you may need to install libevent-dev on your system.
