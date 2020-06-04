import argparse
import importlib
import atexit
from multiprocessing import Pool

print(f'Main call under name {__name__}')

def close_api_gracefully(pool):
    print('Shutting down !')
    pool.terminate()
    pool.join()

parser = argparse.ArgumentParser(description='CL argument for mindsdb server')
parser.add_argument('--api', type=str, default='http,mysql')
parser.add_argument('--config', type=str, default='/etc/mindsdb/config.json')

args = parser.parse_args()
api_arr = args.api.split(',')
pool = Pool(processes=len(api_arr))

for api in api_arr:
    print(api_arr)
    print(f'\n\n\n{api}\n\n\n')
    print(f'Starting Mindsdb {api} API !')
    try:
        start = importlib.import_module(f'mindsdb_server.api.{api}.start')
        pool.apply(func=start.start, args=())
        print(f'Started Mindsdb {api} API ! <clap, clap, clap>')
    except Exception as e:
        close_api_gracefully(pool)
        print(f'Failed to start {api} API with exception {e}')
        exit()


atexit.register(close_api_gracefully, args=(pool))
