import argparse

from mindsdb_server.api.mysql.mysql_proxy.mysql_proxy import MysqlProxy
from mindsdb_server.utilities.config import Config

def start(config):
    config = Config(config)
    MysqlProxy.startProxy(config)

if __name__ == '__main__':
    start()
