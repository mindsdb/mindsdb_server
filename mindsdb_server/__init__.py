import os

from mindsdb_server.utilities.fs import create_dir_struct
from mindsdb_server.utilities.wizards import cli_config

config_dir, predictor_dir, datasource_dir = create_dir_struct()
config_path = os.path.jain(config_store,'config.json')
if not os.path.exists(config_path):
    _ = cli_config(None,None,predictor_dir,datasource_dir,config_dir,use_default=True)

with open(config_path, 'r') as fp:
    os.environ['MINDSDB_STORAGE_PATH'] = json.load(fp)['interface']['mindsdb_native']['storage_dir']


from mindsdb import *
# Figure out how to add this as a module
import lightwood
#import dataskillet
import mindsdb_server.utilities.wizards as wizards
