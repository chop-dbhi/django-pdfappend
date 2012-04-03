# Override a few things here so we can re-use urllib3 dummyserver code 
# to return PDFS
from dummyserver.testcase import HTTPDummyServerTestCase
from dummyserver.handlers import TestingApp, Response
from dummyserver.server import TornadoServerThread
import tornado
import os

class PDFTestingApp(TestingApp):

    def __init__(self, host, port):
        self.port = port
        self.host = host
        TestingApp.__init__(self)

    def pdf(self, request):
        f = open(os.path.join("pdfappend","tests", request.params['file']))
        contents = f.read()
        return Response(body=contents, headers=[("Content-type",
        "application/pdf")])

    def pdf1r(self, request):
        headers = [('Location', "http://%s:%d/pdf1"%(self.host, self.port))]
        return Response(status='301', headers=headers)

    def pdf1(self, request):
        f = open(os.path.join("pdfappend","tests", "one.pdf"))
        contents = f.read()
        return Response(body=contents, headers=[("Content-type",
        "application/pdf")])

    def pdf2(self, request):
        f = open(os.path.join("pdfappend","tests", "two.pdf"))
        contents = f.read()
        return Response(body=contents, headers=[("Content-type",
        "application/pdf")])
    
    def pdf3(self, request):
        f = open(os.path.join("pdfappend","tests", "three.pdf"))
        contents = f.read()
        return Response(body=contents, headers=[("Content-type",
        "application/pdf")])

    def pdf4(self, request):
        f = open(os.path.join("pdfappend","tests", "four.pdf"))
        contents = f.read()
        return Response(body=contents, headers=[("Content-type",
        "application/pdf")])

    def pdf5(self, request):
        f = open(os.path.join("pdfappend","tests", "five.pdf"))
        contents = f.read()
        return Response(body=contents, headers=[("Content-type",
        "application/pdf")])

    def pdf2page(self, request):
        f = open(os.path.join("pdfappend","tests", "twopage.pdf"))
        contents = f.read()
        return Response(body=contents, headers=[("Content-type",
        "application/pdf")])

class TornadoServerThreadPDF(TornadoServerThread):

     def _start_server(self):
        container = tornado.wsgi.WSGIContainer(PDFTestingApp(self.host, self.port))

        if self.scheme == 'https':
            http_server = tornado.httpserver.HTTPServer(container,
                                                        ssl_options=self.certs)
        else:
            http_server = tornado.httpserver.HTTPServer(container)

        http_server.listen(self.port, address=self.host)
        return http_server

class HTTPDummyPDFServerTestCase(HTTPDummyServerTestCase):

    @classmethod
    def _start_server(cls):
        cls.server_thread = TornadoServerThreadPDF(host=cls.host, port=cls.port,
                                                scheme=cls.scheme,
                                                certs=cls.certs)
        cls.server_thread.start()

        # TODO: Loop-check here instead
        import time
        time.sleep(.1)
