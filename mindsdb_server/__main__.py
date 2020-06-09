import argparse
import importlib
import atexit
from multiprocessing import Pool, Process
import os
import traceback

def close_api_gracefully(pool):
    pool.terminate()
    pool.join()

parser = argparse.ArgumentParser(description='CL argument for mindsdb server')
parser.add_argument('--api', type=str, default='http,mysql')
parser.add_argument('--config', type=str, default='/etc/mindsdb/config.json')

args = parser.parse_args()
api_arr = args.api.split(',')
allowed_apis = ['http','mysql']
p_arr = []

for api in api_arr:
    if api not in allowed_apis:
        raise Exception(f'API {api} not in the list of allowed apis: {allowed_apis}')
    try:
        start = importlib.import_module(f'mindsdb_server.api.{api}.start')
        p = Process(target=start.start)
        p.start()
        p_arr.append(p)
        print(f'Started Mindsdb {api} API !')
    except Exception as e:
        print(traceback.format_exc())
        print(f'Failed to start {api} API with exception {e}')

for p in p_arr:
    p.join()

atexit.register(close_api_gracefully, pool=pool)
