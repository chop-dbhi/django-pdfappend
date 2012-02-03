from django.core.cache import cache
from restlib import resources
from django.http import HttpResponse
from pyPdf import PdfFileWriter, PdfFileReader
from email.utils import parsedate_tz, mktime_tz
from email.utils import formatdate
import time
import StringIO
import requests

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

        # We have all the urls, check cache
        headers = lambda h: {"If-None-Match":h.get('etag'),
                "If-Modified-Since":h.get('date')} if h else None

        urls_cache = {url : hit for url, hit in zip(urls, [cache.get(url) for urls in url])}
        urls_needed = {u : True for u,h in urls_cache.items() if h == None or !h['expires']}
        urls_headers = [(u, headers(url_cache[u])) for u in urls_needed.keys()]

        s = requests.session()
        responses = [s.get(url, prefetch=True, headers=h) for u, h in urls_headers]

        self.cache_responses(responses)

        response_cache = {r.url : r for r in responses}

        master_pdf = PdfFileWriter()
        # Iterate over each response and add it to the master PDF
        for url in urls:
            bytes = None
            if urls_needed.has_key(url):
                if response_cache[url].status_code == 200:
                    bytes = response_cache[url].content
                elif response_cache[url].status_code = 304:
                    bytes = urls_cache[url]['data']
                else:
                    # Log a failed response
                    continue
            else:
                bytes = urls_cache[url]['data']
            
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





