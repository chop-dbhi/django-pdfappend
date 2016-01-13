from elasticsearch import Elasticsearch, TransportError
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
        n = datetime.now()
        if get_env_variable('ES_INDEX_APPEND_DATE', False):
            index = self.index + n.strftime("%Y.%m.%d")
        else:
            index = self.index
        date_time = n.strftime("%Y%m%d %H:%M:%S.%f")[:-3]
        self.es.index(index=index, doc_type="logs", body={"message": msg, "date_time": date_time, "environment":self.env, "level":record.levelname.lower()})
 