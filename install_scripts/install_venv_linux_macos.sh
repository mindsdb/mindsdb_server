#!/bin/bash

cd "$SERVER_PATH"
source env/bin/activate
env/bin/pip3 install  pip || env/bin/pip install  pip
env/bin/pip3 install mindsdb  --no-cache-dir || env/bin/pip install mindsdb  --no-cache-dir
env/bin/pip3 install mindsdb-server  --no-cache-dir || env/bin/pip install mindsdb-server  --no-cache-dir
echo "
from mindsdb_server import start_server
if __name__ == '__main__':
    start_server()
" > run_mindsdb_server.py
