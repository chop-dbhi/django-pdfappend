from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic import View
from PyPDF2 import PdfFileWriter, PdfFileReader
from io import BytesIO
from requests_futures.sessions import FuturesSession
import concurrent
import re
import logging

logger = logging.getLogger('pdfappend')

class PDFAppender(View):
    # This assumes a query string is used where a pdfs param
    # is repeatedly used for each PDF we need to concat.
    # Django will create a QueryDict with a pdfs attribute
    # containing all instances of the pdfs attributes used
    # in the query string

    extract_num = re.compile(r'[a-zA-z]+(\d+)')

    def get(self, request, *args, **kwargs):
        # getlist here will return a list of all the query string paramaters
        # named 'pdfs'
        urls = request.GET.getlist("pdfs")
        print(urls)
        if not urls:
            items = request.GET.items()
            try:
                items.sort(key=lambda x:int(self.extract_num.match(x[0]).group(1)))
            except:
                logger.error("Bad query string: %s" % items)
                return HttpResponseBadRequest("Invalid query string")
            urls = []
            for key, value in items:
               urls.append(value)
               
        session = FuturesSession(executor=concurrent.futures.ThreadPoolExecutor(max_workers=5))
        master_pdf = PdfFileWriter()
        
        waiting  = [session.get(url, allow_redirects=True) for url in urls]
        
        complete, incomplete = concurrent.futures.wait(waiting, timeout=15, return_when=concurrent.futures.ALL_COMPLETED)
        
        for f in complete:
            error = f.exception()
            if error != None:
                logger.error("Error retrieving url: %s" % error)
                continue
            
            response = f.result()
            if response.status_code != 200:
                print(response.status_code)
                continue
            content = response.content
            # pyPDF needs a file like object
            input = PdfFileReader(BytesIO(content))
            # Add this whole PDF to the master PDF
            for page_no in range(0, input.numPages):
                master_pdf.addPage(input.getPage(page_no))
        
        for f in incomplete:
            logger.error("Timeout retrieving url: %s" % f)

        output = HttpResponse(content_type="application/pdf")
        master_pdf.write(output)
        return output