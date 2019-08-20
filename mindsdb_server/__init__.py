import sys
if sys.version_info < (3,6):
    sys.exit('Sorry, For MindsDB Server does not support python < 3.6')


from mindsdb_server.server import start_server
