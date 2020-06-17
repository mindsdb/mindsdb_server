print('loading entrypoint')
import torch
def script_method(fn, _rcb=None):
    return fn
def script(obj, optimize=True, _frames_up=0, _rcb=None):
    return obj
import torch.jit
torch.jit.script_method = script_method
torch.jit.script = script


import mindsdb
from mindsdb import libs

print('running main')
import argparse
import importlib
import atexit
from torch.multiprocessing import Process, get_start_method, set_start_method
import os
import traceback
import time
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
        try:
            os.system('fuser -k 3306/tcp')
        except Exception:
            pass

        try:
            os.system('fuser -k 47334/tcp')
            sys.stdout.flush()
        except Exception:
            pass
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

try:
    os.system('fuser -k 3306/tcp')
except Exception:
    pass

try:
    os.system('fuser -k 47334/tcp')
    sys.stdout.flush()
except Exception:
    pass

start_functions = {
    'http': start_http,
    'mysql': start_mysql
}

for api in api_arr:
    print(api_arr)
    print(f'\n\n\n{api}\n\n\n')
    print(f'Starting Mindsdb {api} API !')
    try:
        p = Process(target=start_functions[api], args=(config_path,))
        p.start()
        p_arr.append(p)
        print(f'Started Mindsdb {api} API !')
    except BaseException:
        close_api_gracefully(p_arr)
        print(f'Failed to start {api} API with exception {e}')
        print(traceback.format_exc())
        exit()
    finally:
        close_api_gracefully(p_arr)

atexit.register(close_api_gracefully, p_arr=p_arr)

for p in p_arr:
    p.join()
