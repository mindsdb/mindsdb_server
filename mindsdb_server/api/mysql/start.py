from mindsdb_server.api.mysql.mysql_proxy.mysql_proxy import MysqlProxy

def start():
    MysqlProxy.startProxy()

if __name__ == '__main__':
    start()
