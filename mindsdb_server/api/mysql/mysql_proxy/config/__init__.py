
import os
import logging


def ifEnvElse(env_var, else_value):
    """
    return else_value if env_var is not set in environment variables
    :return:
    """
    return else_value if env_var not in os.environ else os.environ[env_var]


PROXY_SERVER_PORT = ifEnvElse('MINDSDB_PROXY_SERVER_PORT', 3306)
PROXY_SERVER_HOST = ifEnvElse('MINDSDB_PROXY_SERVER_HOST', 'localhost')

PROXY_LOG_CONFIG = {
    'format': ifEnvElse('MINDSDB_PROXY_LOG_FORMAT', '[%(levelname)s] %(message)s'),
    'filename': ifEnvElse('MINDSDB_PROXY_LOG_FILENAME', 'app.log'),
    'file_level': ifEnvElse('MINDSDB_PROXY_LOG_LEVEL', logging.INFO),
    'console_level': logging.INFO,
}

CERT_PATH = 'cert.pem'
