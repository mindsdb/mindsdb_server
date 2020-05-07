#!/bin/bash



cd "${SERVER_PATH}"

source env/bin/activate
env/bin/pip3 install --upgrade pip || env/bin/pip install --upgrade pip
env/bin/pip3 install lightwood --upgrade  || env/bin/pip install lightwood --upgrade
env/bin/pip3 install mindsdb --upgrade  || env/bin/pip install mindsdb --upgrade
env/bin/pip3 install mindsdb-server --upgrade  || env/bin/pip install mindsdb-server --upgrade
echo "
from mindsdb_server import start_server
if __name__ == '__main__':
    start_server()
" > run_mindsdb_server.py
