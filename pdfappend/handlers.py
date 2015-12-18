from elasticsearch import Elasticsearch
from datetime import datetime
import logging

class ESHandler(logging.Handler):
    
    def __init__(self, index, host, port):
        logging.Handler.__init__(self)
        self.index = index
        self.es = Elasticsearch(['%s:%d' % (host, port)])
    
    def emit(self, record):
        msg = self.format(record)
        self.es.index(index=self.index, doc_type="log", body={"message": msg, "timestamp": datetime.now()})