#!/bin/bash

"$PYPATH" -m pip install --user --upgrade pip
"$PYPATH" -m pip install --user virtualenv

mkdir "$SERVER_PATH"
cd "$SERVER_PATH"
"$PYPATH" -m virtualenv env --python="$PYPATH"
source env/bin/activate
pip install --upgrade pip || pip3 install --upgrade pip
pip install mindsdb --upgrade --no-cache-dir || pip3 install mindsdb --upgrade --no-cache-dir
pip install mindsdb-server --upgrade --no-cache-dir || pip3 install mindsdb-server --upgrade --no-cache-dir
echo "
from mindsdb_server import start_server
if __name__ == '__main__':
    start_server()
" > run_mindsdb_server.py
