import argparse

from mindsdb_server.utilities.config import config
from mindsdb_server.api.mysql.mysql_proxy.mysql_proxy import MysqlProxy

def start():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='/etc/mindsdb/config.json')
    args = parser.parse_args()
    config.merge(args.config)

    MysqlProxy.startProxy()

if __name__ == '__main__':
    start()
