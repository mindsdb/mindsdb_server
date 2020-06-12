import sys
import os
from pathlib import Path
import time

install_as  = sys.argv[1]
python_path = sys.argv[2]
pip_path    = sys.argv[3]

current_dir = os.path.dirname(os.path.realpath(__file__))
root_dir = Path(current_dir).parents[1]

if install_as == 'user':
    config_dir = os.path.join(root_dir,'data', 'config')
    storage_dir = os.path.join(root_dir,'data', 'storage')
else:
    config_dir = os.path.join('/etc/mindsdb/')
    storage_dir = os.path.join('/var/lib/mindsdb/')

os.makedirs(config_dir,exist_ok=True)
os.makedirs(storage_dir,exist_ok=True)

print(f'Configuration files will be stored in {config_dir}')
print(f'Datasources and predictors will be stored in {storage_dir}')

datasource_dir = os.path.join(storage_dir,'datasources')
predictor_dir = os.path.join(storage_dir,'predictors')
# @TODO Deal with permissions stuff

os.makedirs(datasource_dir,exist_ok=True)
os.makedirs(predictor_dir,exist_ok=True)

print(f'\nInstalling some large dependencies via pip ({pip_path}), this might take a while\n')
time.sleep(3)


# How it installs itself (maybe instead of github just use local download if user has cloned everything ?)
if install_as == 'user':
    os.system(f'{pip_path} install --user git+https://github.com/mindsdb/mindsdb_server.git@split --upgrade --force-reinstall')
else:
    os.system(f'sudo {pip_path} install git+https://github.com/mindsdb/mindsdb_server.git@split --upgrade --force-reinstall')

branch = 'master' # In the future this will be `stable`
dataskillet_source = None
lightwood_source = f'git+https://github.com/mindsdb/lightwood.git@{branch}'
mindsdb_source = f'git+https://github.com/mindsdb/mindsdb.git@{branch}'

for source in [dataskillet_source,lightwood_source,mindsdb_source]:
    if isinstance(source,str):
        if install_as == 'user':
            os.system(f'{pip_path} install --user {source} --upgrade --force-reinstall')
        else:
            os.system(f'sudo {pip_path} install {source} --upgrade --force-reinstall')
time.sleep(1)
print('Done installing dependencies')
print('\nLast step: Configure Mindsdb\n')

from mindsdb_server.utilities.wizards import cli_config,daemon_creator
config_path = cli_config(python_path,pip_path,predictor_dir,datasource_dir,config_dir)
daemon_creator(python_path,config_path)
