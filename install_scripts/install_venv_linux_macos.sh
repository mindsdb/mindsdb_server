#!/bin/bash
"$PYPATH" -m pip install --user --upgrade pip;
"$PYPATH" -m pip install --user virtualenv;
mkdir -p "$SERVER_PATH" || mkdir "$SERVER_PATH";

cd "$SERVER_PATH";

"$PYPATH" -m virtualenv env --python="$PYPATH";

echo "."$SERVER_PATH"/env/bin/activate";

source "."$SERVER_PATH"/env/bin/activate";

echo "."$SERVER_PATH"/env/bin/activate";

"."$SERVER_PATH"/env/bin/pip3" install --upgrade pip || "."$SERVER_PATH"/env/bin/pip" install --upgrade pip
"."$SERVER_PATH"/env/bin/pip3" install mindsdb  --no-cache-dir || "."$SERVER_PATH"/env/bin/pip" install mindsdb  --no-cache-dir
"."$SERVER_PATH"/env/bin/pip3" install mindsdb-server  --no-cache-dir || "."$SERVER_PATH"/env/bin/pip" install mindsdb-server  --no-cache-dir
echo "
from mindsdb_server import start_server
if __name__ == '__main__':
    start_server()
" > run_mindsdb_server.py;
