print('Running entrypoint')

"""Disable torch.jit, pyinstaller can't work with it."""
def script_method(fn, _rcb=None):
    return fn
def script(obj, optimize=True, _frames_up=0, _rcb=None):
    return obj
import torch.jit
torch.jit.script_method = script_method
torch.jit.script = script

import argparse
import atexit
from torch.multiprocessing import Process
import os
import sys

from mindsdb_server.utilities.config import Config
from mindsdb_server.api.http.start import start as start_http
from mindsdb_server.api.mysql.start import start as start_mysql

print(f'Entrypoint call under name {__name__}')


def close_api_gracefully(p_arr):
    for p in p_arr:
        sys.stdout.flush()
        p.terminate()
        p.join()
        sys.stdout.flush()


parser = argparse.ArgumentParser(description='CL argument for mindsdb server')
parser.add_argument('--api', type=str, default=None)
parser.add_argument('--config', type=str, default='mindsdb_server/default_config.json')

args = parser.parse_args()

config_path = args.config
config = Config(config_path)

if args.api is None:
    api_arr = [api for api in config['api']]
else:
    api_arr = args.api.split(',')


p_arr = []

start_functions = {
    'http': start_http,
    'mysql': start_mysql
}

for api in api_arr:
    print(f'Starting Mindsdb {api} API !')
    try:
        p = Process(target=start_functions[api], args=(config_path,))
        p.start()
        p_arr.append(p)
        print(f'Started Mindsdb {api} API !')
    except BaseException as e:
        close_api_gracefully(p_arr)
        print(f'Failed to start {api} API with exception {e}')
        raise

atexit.register(close_api_gracefully, p_arr=p_arr)

for p in p_arr:
    p.join()
