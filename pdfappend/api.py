from django.conf import settings
from django.core.cache import get_cache
from restlib import resources
from django.http import HttpResponse, HttpResponseBadRequest
from pyPdf import PdfFileWriter, PdfFileReader
from email.utils import parsedate_tz, mktime_tz
from email.utils import formatdate
from urlparse import urlparse
from StringIO import StringIO
from urllib3 import connection_from_url, PoolManager
from urllib3.connectionpool import HostChangedError
import workerpool
import Queue
import time
import re

# If only requesting pdfs from one host
# number requests above which threading
# will be enabled
try:
    CONCURRENCY_THRESHOLD = settings.PDFAPPEND_CONCURRENCY_THRESHOLD
except:
    CONCURRENCY_THRESHOLD = 3

# Maximum number of simultaneous connections to a single
try:
    CONNECTIONS_PER_HOST = settings.PDFAPPEND_CONNECTIONS_PER_HOST
except:
    CONNECTIONS_PER_HOST = 6

# Maximum threads to be used simultaneously for a request
try:
    MAX_THREADS = settings.PDFAPPEND_MAX_THREADS
except:
    MAX_THREADS = 12

cache_enabled = False

if settings.CACHES.has_key("pdfappend"):
    cache_enabled = True

# quick little snippet figure out which http headers 
# to use depending on what values are in the cache
headers = lambda h: dict((attr,h.get(v))
    for attr, v in
    [("If-None-Match", "etag"), ("If-Modified-Since", "date")]
    if h and h.get(v))

class GetFile(workerpool.Job):
    def __init__(self, queue, connection_pool, url, headers):
        self.queue = queue
        self.pool = connection_pool
        self.url = url
        self.headers = headers

    def run(self):
        try: 
           response = self.pool.request("GET", self.url, headers=self.headers)
        except HostChangedError, e:
           # Redirect, give up on managing resources ourselves, just get the
           # file
           managed_pool = PoolManager(1)
           response = managed_pool.request('GET', e.url, headers = self.headers)
        self.queue.put((self.url, response))

class PDFAppender(resources.Resource):
    # This assumes a query string is used where a pdfs param
    # is repeatedly used for each PDF we need to concat.
    # Django will create a QueryDict with a pdfs attribute
    # containing all instances of the pdfs attributes used
    # in the query string

    extract_num = re.compile(r'[a-zA-z]+(\d+)')

    def GET(self, request):
        # getlist here will return a list of all the query string paramaters
        # named 'pdfs'
        urls = request.GET.getlist("pdfs")
        if not urls:
            items = request.GET.items()
            try:
                items.sort(key=lambda x:int(self.extract_num.match(x[0]).group(1)))
            except:
                return HttpResponseBadRequest("Invalid query string.")
            urls = []
            for key, value in items:
               urls.append(value)

        if cache_enabled:
            cache = get_cache('pdfappend')
            # Create dictionary of url:<cache value>
            urls_cache = dict((url, hit) for url, hit in zip(urls,
                [cache.get(url) for url in urls]))
            # Determine which urls need to be requested
            urls_needed = dict((url,True) for url, hit in urls_cache.items() if
                    hit == None or not hit.has_key('expires'))
            # Create array of [(url, <header dict>)] for urls that need to be
            # requested
            urls_headers = [(url, headers(urls_cache[url]))
                    for url in urls_needed.keys()]
        else:
            urls_headers = [(url, {}) for url in urls]

        hosts = self.sortByHost(urls_headers)

        # A couple of things here. If we have more than 1 host, we will spawn 
        # a thread, but if there is only one host, we may refrain depending on 
        # the following:
        # If connections per host is 1, we won't spawn a thread
        # If there are <= 3 URLS being requested, we will not spawn a thread, 
        # just use a keepalive HTTP session and make the requests sequentially
        if (len(hosts) > 1 or len(hosts[0]) > CONCURRENCY_THRESHOLD):
            responses = self.getConcurrent(hosts)
        else:
            responses = self.getSequential(hosts[0])

        if cache_enabled: 
            self.cache_responses(responses, cache)

        response_cache = dict((u, r) for u,r in responses)

        master_pdf = PdfFileWriter()

        # Iterate over each pdf and add it to the master PDF
        for url in urls:
            if cache_enabled:
                if urls_needed.has_key(url):
                    if response_cache[url].status == 200:
                        raw_bytes = response_cache[url].data
                    elif response_cache[url].status == 304:
                        raw_bytes = urls_cache[url]['data']
                    else:
                        # Log a failed response?
                        continue
                else:
                    raw_bytes = urls_cache[url]['data']
            else:
                # Verify request succeeded
                if not response_cache[url].status == 200:
                    # Log failed response?
                    continue
                raw_bytes = response_cache[url].data

            # pyPDF needs a file like object
            input = PdfFileReader(StringIO(raw_bytes))

            # Add this whole PDF to the master PDF
            for page_no in range(0, input.numPages):
                master_pdf.addPage(input.getPage(page_no))

        output = HttpResponse(content_type="application/pdf")
        master_pdf.write(output)
        return output

    def cache_responses(self, responses, cache):
        cacheable = [(u, r) for u, r in responses if r.status == 200]
        for u, r in cacheable:
            obj = {}
            if r.headers['Expires']:
                cache.set(u, {
                    'expires': True,
                    'data': r. data
                    },
                    mktime_tz(parsedate_tz(r.headers['Expires'])) -
                    time.time()
                )
            else:
                cache.set(u, {
                    'data':r.data,
                    'etag':r.headers.get('Etag', None),
                    'date':formatdate()
                })


    def sortByHost(self, urls_headers):
        hosts = {}
        for url, header in urls_headers:
            parts = urlparse(url)
            hosts.setdefault(parts.netloc, []).append((url,header))
        return hosts.values()

    def getConcurrent(self, hosts):
        job_pool = workerpool.WorkerPool(size=MAX_THREADS)
        results = Queue.Queue()

        for host in hosts:
            conn_pool = connection_from_url(host[0][0],
                    maxsize=CONNECTIONS_PER_HOST)
            for url, headers in host:
                job = GetFile(results, conn_pool, url, headers)
                job_pool.put(job)

        job_pool.shutdown()
        job_pool.join()

        responses = []
        while (not results.empty()):
            responses.append(results.get())
        return responses

    def getSequential(self, urls_headers):
        conn_pool = connection_from_url(urls_headers[0][0],
                maxsize=CONNECTIONS_PER_HOST)
        responses = []

        for url, headers in urls_headers:
            try:
                response = conn_pool.request("GET", url, headers = headers)
            except HostChangedError, e:
               # Redirect, give up on managing resources ourselves, just get the
               # file
               managed_pool = PoolManager(1)
               response = managed_pool.request('GET', e.url, headers = headers)
            responses.append((url, response))
        return responses



