from django.conf import settings
from django.core.cache import get_cache
from restlib import resources
from django.http import HttpResponse
from pyPdf import PdfFileWriter, PdfFileReader
from email.utils import parsedate_tz, mktime_tz
from email.utils import formatdate
import time
import StringIO
import requests

cache_enable = False
if settings.CACHES.has_key("pdfappend"):
    cache_enabled = True

headers = lambda h: {
            "If-None-Match": h.get('etag'),
            "If-Modified-Since": h.get('date')} if h else None

class PDFAppender(resources.Resource):

    # This assumes a query string is used where a pdfs param
    # is repeatedly used for each PDF we need to concat.
    # Django will create a QueryDict with a pdfs attribute
    # containing all instances of the pdfs attributes used
    # in the query string
    def GET(self, request):
        # getlist here will return a list of all the query string paramaters
        # named 'pdfs'
        urls = request.GET.getlist("pdfs")
        if not urls:
            items = request.GET.items()
            items.sort(key=lambda x: x[0])
            urls = []
            for key, value in items:
               urls.append(value)

        if cache_enabled:
            cache = get_cache('pdfappend')
            urls_cache = dict((url, hit) for url, hit in zip(urls,
                [cache.get(url) for urls in url]))
            urls_needed = dict((url,True) for url, hit in urls_cache.items()
                    if hit == None or !hit['expires'])
            urls_headers = [(url, headers(url_cache[url]))
                    for url in urls_needed.keys()]
        else:
            urls_headers = [(url, {}) for url in urls]

        s = requests.session()
        responses = [s.get(url, prefetch=True, headers=h) 
                for u, h in urls_headers]

        self.cache_responses(responses)

        response_cache = dict((r.url, r) for r in responses)

        master_pdf = PdfFileWriter()

        # Iterate over each pdf and add it to the master PDF
        for url in urls:
            if cache_enabled:
                if urls_needed.has_key(url):
                    if response_cache[url].status_code == 200:
                        bytes = response_cache[url].content
                    elif response_cache[url].status_code = 304:
                        bytes = urls_cache[url]['data']
                    else:
                        # Log a failed response?
                        continue
                else:
                    bytes = urls_cache[url]['data']
            else:
                # Verify request succeeded
                if not response_cache[url].status_code == 200:
                    # Log failed response?
                    continue
                bytes = response_cache[url].content

            # pyPDF needs a file like object
            input = PdfFileReader(StringIO.StringIO(bytes))

            # Add this whole PDF to the master PDF
            for page_no in range(0, input.numPages):
                master_pdf.addPage(input.getPage(page_no))

        output = HttpResponse(content_type="application/pdf")
        master_pdf.write(output)
        return output

    def cache_responses(self, response):
        cacheable = [r for r in responses if r.status_code == 200]
        for r in cacheable:
            obj = {}
            if r.headers['Expires']:
                cache.set(response.request.url,
                    {
                        'expires': True,
                        'data': response.content
                    },
                    mktime_tz(parsedate_tz(r.headers['Expires'])) -
                    time.time())
            else:
                cache.set(response.request.url,
                    {
                        'data':response.content,
                        'etag':response.headers['Etag']
                        'date':formatdate()
                    })
