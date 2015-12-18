from elasticsearch import Elasticsearch
from datetime import datetime
import logging
import os

def get_env_variable(var_name, default=None):
    """ Get the environment variable or return an exception"""
    try:
        return os.environ[var_name]
    except KeyError:
        return default

class ESHandler(logging.Handler):
    
    def __init__(self, index, host, port):
        logging.Handler.__init__(self)
        self.index = index
        self.es = Elasticsearch(['%s:%d' % (host, port)])
        self.env = get_env_variable("APP_ENV", "unspecified")
    
    def emit(self, record):
        msg = self.format(record)
        self.es.index(index=self.index, doc_type="log", body={"message": msg, "timestamp": datetime.now(), "environment":self.env})