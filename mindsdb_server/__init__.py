import sys
if sys.version_info < (3,3):
    sys.exit('Sorry, For MindsDB Server does not support python < 3.3')


from mindsdb_server.server import app as server




