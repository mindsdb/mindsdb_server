from mindsdb_server.api.mysql.mysql_proxy.datasources.ray_datasource_wrapper import RayDataSourceWrapper
from mindsdb_server.api.mysql.mysql_proxy.datasources.information_schema import InformationSchema
from mindsdb_server.api.mysql.mysql_proxy.datasources.mindsdb_datasource import MindsDBDataSource
from mindsdb_server.api.mysql.mysql_proxy.datasources.mongo_datasource import MongoDataSource
from mindsdb_server.api.mysql.mysql_proxy.datasources.csv_datasource import CSVDataSource
from mindsdb_server.utilities.config import read as read_config

config = read_config()
all_ds = config['mysql'].get('datasources', [])

datasources = InformationSchema()

datasources.add({
    'mindsdb': RayDataSourceWrapper(MindsDBDataSource.remote())
})

csv_ds = [x for x in all_ds if x['type'].lower() == 'csv']
for ds in csv_ds:
    datasources.add({
        ds['name']: RayDataSourceWrapper(
            CSVDataSource.remote(ds['files'])
        )
    })

mongo_ds = [x for x in all_ds if x['type'].lower() == 'mongo']
for ds in mongo_ds:
    datasources.add({
        ds['name']: RayDataSourceWrapper(
            MongoDataSource.remote(ds['host'], ds['port'], ds['database'])
        )
    })

