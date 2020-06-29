#!/bin/bash
cd "${SERVER_PATH}"

. env/bin/activate
env/bin/pip3 install --upgrade pip || env/bin/pip install --upgrade pip
env/bin/pip3 install mindsdb --upgrade  || env/bin/pip install mindsdb --upgrade
echo "
import runpy
import torch.multiprocessing as mp

if __name__ == '__main__':
  mp.freeze_support()
  runpy.run_module('mindsdb',run_name='__main__')
" > run_mindsdb_server.py
