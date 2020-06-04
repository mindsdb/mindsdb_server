from mindsdb_server.api.http.namespaces.predictor import ns_conf as predictor_ns
from mindsdb_server.api.http.namespaces.datasource import ns_conf as datasource_ns
from mindsdb_server.api.http.namespaces.util import ns_conf as utils_ns
from mindsdb_server.api.http.shared_ressources import get_shared
import json
import os
import mindsdb
import logging
import sys


def start():
    # Source from config later
    from_tests=False
    port=None
    host=None
    storage_path=''
    debug=True

    if not logging.root.handlers:
        rootLogger = logging.getLogger()

        outStream = logging.StreamHandler(sys.stdout)
        outStream.addFilter(lambda record: record.levelno <= logging.INFO)
        rootLogger.addHandler(outStream)

        errStream = logging.StreamHandler(sys.stderr)
        errStream.addFilter(lambda record: record.levelno > logging.INFO)
        rootLogger.addHandler(errStream)

    if port is None:
        port = 47334

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

    # return only app for tests to use test_client
    if from_tests:
        return app

    app.run(debug=debug, port=port, host=host)
