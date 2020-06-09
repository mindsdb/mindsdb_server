import argparse
import importlib
import atexit
from multiprocessing import Pool, Process
import os
import traceback

from mindsdb_server.utilities import config

print(f'Main call under name {__name__}')

def close_api_gracefully(pool):
    print('Shutting down !')
    pool.terminate()
    pool.join()

parser = argparse.ArgumentParser(description='CL argument for mindsdb server')
parser.add_argument('--api', type=str, default='http,mysql') # alternative when mysql api is ready: default='http,mysql'
parser.add_argument('--config', type=str, default='/etc/mindsdb/config.json')

args = parser.parse_args()
config.merge(args.config)
api_arr = args.api.split(',')
pool = Pool(processes=len(api_arr))

p_arr = []

for api in api_arr:
    print(api_arr)
    print(f'\n\n\n{api}\n\n\n')
    print(f'Starting Mindsdb {api} API !')
    try:
        start = importlib.import_module(f'mindsdb_server.api.{api}.start')
        p = Process(target=start.start)
        p.start()
        p_arr.append(p)
        print(f'Started Mindsdb {api} API ! <clap, clap, clap>')
    except Exception as e:
        #close_api_gracefully(pool)
        print(f'Failed to start {api} API with exception {e}')
        print(traceback.format_exc())
        #exit()

for p in p_arr:
    print(p)
    import time
    time.sleep(40)
    p.join()

atexit.register(close_api_gracefully, pool=pool)