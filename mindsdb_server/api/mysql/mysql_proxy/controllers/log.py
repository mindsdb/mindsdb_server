import os
import logging
from logging.handlers import RotatingFileHandler
from mindsdb_server.api.mysql.mysql_proxy.config import PROXY_LOG_CONFIG as config

def init_logger(nolog=False):
    if not os.path.exists('./logs'):
        os.makedirs('./logs')

    logger = logging.getLogger('app')
    logger.setLevel(min(config['console_level'], config['file_level']))

    fh = RotatingFileHandler(
        os.path.join('logs', config['filename']),
        mode='a',
        encoding=config.get('encoding', 'utf-8'),
        maxBytes=100*1024,
        backupCount=3
    )
    fh.setLevel(config['file_level'])

    # create console handler
    ch = logging.StreamHandler()
    ch.setLevel(config['console_level'])

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

log = logging.getLogger('app')
