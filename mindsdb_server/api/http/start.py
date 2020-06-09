from mindsdb_server.api.http.namespaces.predictor import ns_conf as predictor_ns
from mindsdb_server.api.http.namespaces.datasource import ns_conf as datasource_ns
from mindsdb_server.api.http.namespaces.util import ns_conf as utils_ns
from mindsdb_server.api.http.shared_ressources import get_shared
import json
import os
import mindsdb
import logging
import sys
import random

def start():
    port=47334
    host='0.0.0.0'
    debug=False

    if not logging.root.handlers:
        rootLogger = logging.getLogger()

        outStream = logging.StreamHandler(sys.stdout)
        outStream.addFilter(lambda record: record.levelno <= logging.INFO)
        rootLogger.addHandler(outStream)

        errStream = logging.StreamHandler(sys.stderr)
        errStream.addFilter(lambda record: record.levelno > logging.INFO)
        rootLogger.addHandler(errStream)


    mindsdb.CONFIG.MINDSDB_DATASOURCES_PATH = os.path.join(mindsdb.CONFIG.MINDSDB_STORAGE_PATH,'datasources')
    mindsdb.CONFIG.MINDSDB_TEMP_PATH = os.path.join(mindsdb.CONFIG.MINDSDB_STORAGE_PATH,'tmp')

    os.makedirs(mindsdb.CONFIG.MINDSDB_STORAGE_PATH, exist_ok=True)
    os.makedirs(mindsdb.CONFIG.MINDSDB_DATASOURCES_PATH, exist_ok=True)
    os.makedirs(mindsdb.CONFIG.MINDSDB_TEMP_PATH, exist_ok=True)
    #'''
    app, api = get_shared()

    api.add_namespace(predictor_ns)
    api.add_namespace(datasource_ns)
    api.add_namespace(utils_ns)


    app.run(debug=debug, port=port, host=host)

if __name__ == '__main__':
    start()
