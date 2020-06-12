from mindsdb_server.api.mysql.mysql_proxy.datasources.information_schema import InformationSchema
from mindsdb_server.api.mysql.mysql_proxy.datasources.mindsdb_datasource import MindsDBDataSource
from mindsdb_server.api.mysql.mysql_proxy.datasources.mongo_datasource import MongoDataSource
from mindsdb_server.api.mysql.mysql_proxy.datasources.csv_datasource import CSVDataSource


def init_datasources(config):
    all_ds = config['api']['mysql'].get('datasources', [])

    datasources = InformationSchema()

    datasources.add({
        'mindsdb': MindsDBDataSource()
    })

    csv_ds = [x for x in all_ds if x['type'].lower() == 'csv']
    for ds in csv_ds:
        datasources.add({
            ds['name']: CSVDataSource(ds['files'])
        })

    mongo_ds = [x for x in all_ds if x['type'].lower() == 'mongo']
    for ds in mongo_ds:
        datasources.add({
            ds['name']: MongoDataSource(ds['host'], ds['port'], ds['database'])
        })
    return datasources
