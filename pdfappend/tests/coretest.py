#!/usr/bin/env python
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.client import Client
from pyPdf import PdfFileReader
from StringIO import StringIO
import testserver

# request = self.factory.get('/customer/details')

# Test my_view() as if it were deployed at /customer/details
# response = my_view(request)

__all__ = ('PDFTestNoCache',)

def pdfNumPages(content):
    pdf = PdfFileReader(StringIO(content))
    return pdf.getNumPages()

class PDFTestNoCache(testserver.HTTPDummyPDFServerTestCase):
    c = Client()

    # Request two pdfs using the pdfs paramater, as opposed to number
    # pdf1..pdfN params
    # PDF urls contain query string
    def test_2_pdfs_qs(self):
        response = self.c.get("/api/?pdfs=http://%s:%d/pdf?file=one.pdf&pdfs=http://%s:%d/pdf?file=two.pdf"
                % ((self.host, self.port) * 2), follow = True, HTTP_ACCEPT="application/*")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(pdfNumPages(response.content), 2)

    # Request two pdfs using the pdfs paramater, as opposed to number
    # pdf1..pdfN params
    # PDF urls do not contain query string
    def test_2_pdfs(self):
        response = self.c.get("/api/?pdfs=http://%s:%d/pdf1&pdfs=http://%s:%d/pdf2" 
                % ((self.host,self.port) * 2), follow = True, HTTP_ACCEPT="application/*")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(pdfNumPages(response.content), 2)

    def test_2_pdfs_2page(self):
        response = self.c.get("/api/?pdfs=http://%s:%d/pdf1&pdfs=http://%s:%d/pdf2page" 
                % ((self.host,self.port) * 2), follow = True, HTTP_ACCEPT="application/*")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(pdfNumPages(response.content), 3)

    def test_1_pdfs(self):
        response = self.c.get("/api/?pdfs=http://%s:%d/pdf1" % 
                (self.host,self.port), follow = True, HTTP_ACCEPT="application/*")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(pdfNumPages(response.content), 1)

    # By default > 3 requests to one server are executed concurrently
    def test_5_pdfs_conc(self):
        req_urls = ["pdfs=http://%s:%d/pdf1",
                    "pdfs=http://%s:%d/pdf2",
                    "pdfs=http://%s:%d/pdf3",
                    "pdfs=http://%s:%d/pdf4",
                    "pdfs=http://%s:%d/pdf5"]
        response = self.c.get("/api/?"+"&".join(req_urls)
                % ((self.host, self.port) * len(req_urls)), follow = True, 
                HTTP_ACCEPT="application/*")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(pdfNumPages(response.content), 5)

    def test_1_pdfs_redirect(self):
        response = self.c.get("/api/?pdfs=http://%s:%d/pdf1r" % 
                (self.host,self.port), follow = True, HTTP_ACCEPT="application/*")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(pdfNumPages(response.content), 1)


    def test_2_pdfs_1_redirect(self):
        response = self.c.get("/api/?pdfs=http://%s:%d/pdf1r&pdfs=http://%s:%d/pdf2page" %
                ((self.host,self.port)*2), follow = True, HTTP_ACCEPT="application/*")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(pdfNumPages(response.content), 3)

    def test_5_pdfs_conc_1_redirect(self):
        req_urls = ["pdfs=http://%s:%d/pdf2",
                    "pdfs=http://%s:%d/pdf1r",
                    "pdfs=http://%s:%d/pdf3",
                    "pdfs=http://%s:%d/pdf4",
                    "pdfs=http://%s:%d/pdf5"]
        response = self.c.get("/api/?"+"&".join(req_urls)
                % ((self.host, self.port) * len(req_urls)), follow = True, 
                HTTP_ACCEPT="application/*")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(pdfNumPages(response.content), 5)

    def test_1_pdfs_redirect_domain(self):
        response = self.c.get("/api/?pdfs=http://%s:%d/pdf1r" % 
                (self.host_alt, self.port), follow = True, HTTP_ACCEPT="application/*")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(pdfNumPages(response.content), 1)


    def test_5_pdfs_conc_1_redirectdomain(self):
        req_urls = ["pdfs=http://%s:%d/pdf2",
                    "pdfs=http://%s:%d/pdf1r" % (self.host_alt, self.port),
                    "pdfs=http://%s:%d/pdf3",
                    "pdfs=http://%s:%d/pdf4",
                    "pdfs=http://%s:%d/pdf5"]
        response = self.c.get("/api/?"+"&".join(req_urls)
                % ((self.host, self.port) * (len(req_urls)-1)), follow = True, 
                HTTP_ACCEPT="application/*")



