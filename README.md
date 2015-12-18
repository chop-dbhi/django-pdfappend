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
