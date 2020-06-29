#!/bin/bash
"${PYPATH}" -m pip install --user --upgrade pip
"${PYPATH}" -m pip install --user virtualenv
mkdir -p "${SERVER_PATH}" || mkdir "${SERVER_PATH}"

cd "${SERVER_PATH}"

"${PYPATH}" -m virtualenv env --python="${PYPATH}"

. env/bin/activate
env/bin/pip3 install --upgrade pip || env/bin/pip install --upgrade pip
env/bin/pip3 install mindsdb  --no-cache-dir || env/bin/pip install mindsdb  --no-cache-dir
echo "
import runpy
runpy.run_module('mindsdb')
" > run_mindsdb_server.py
