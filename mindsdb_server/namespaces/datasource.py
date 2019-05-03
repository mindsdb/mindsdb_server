from flask_restplus import Resource, fields

from mindsdb_server.namespaces.configs.datasources import ns_conf
from mindsdb_server.namespaces.entitites.datasources.datasource import (
    datasource_metadata,
    put_datasource_params,
    post_datasource_params,
    EXAMPLES as DATASOURCES_LIST_EXAMPLE
)
from mindsdb_server.namespaces.entitites.datasources.datasource_data import (
    get_datasource_rows_params,
    datasource_rows_metadata,
    EXAMPLES as GET_DATASOURCE_ROWS_EXAMPLES
)
from mindsdb_server.namespaces.entitites.datasources.datasource_files import (
    put_datasource_file_params
)
from mindsdb_server.namespaces.entitites.datasources.datasource_missed_files import (
    datasource_missed_files_metadata,
    get_datasource_missed_files_params,
    EXAMPLES as GET_DATASOURCE_MISSED_FILES_EXAMPLES
)

from mindsdb_server.shared_ressources import get_shared
import json
import datetime
from dateutil.parser import parse
import os

app, api = get_shared()
datasources = []


def get_datasource():
    datasources = []
    for file in os.listdir('storage'):
        if 'datasource' in file:
            print(file)
            with open('storage/' + file, 'r') as fp:
                datasource = json.load(fp)
                datasource['created_at'] = parse(datasource['created_at'])
                datasource['update_at'] = parse(datasource['update_at'])
                datasources.append(datasource)
    return datasources


@ns_conf.route('/')
class DatasourcesList(Resource):
    @ns_conf.doc('get_atasources_list')
    @ns_conf.marshal_list_with(datasource_metadata)
    def get(self):
        '''List all datasources'''
        return get_datasource()

@ns_conf.route('/<name>')
@ns_conf.param('name', 'Datasource name')
class Datasource(Resource):
    @ns_conf.doc('get_datasource')
    @ns_conf.marshal_with(datasource_metadata)
    def get(self, name):
        '''return datasource metadata'''
        data_sources = get_datasource()
        for ds in data_sources:
            if ds.name == name:
                return ds
        return None

    @ns_conf.doc('post_datasource', params=post_datasource_params)
    def post(self):
        '''update datasource attributes'''
        return '', 404

    @ns_conf.doc('delete_datasource')
    def delete(self, name):
        '''delete datasource'''
        return '', 404

    @ns_conf.doc('put_datasource', params=put_datasource_params)
    @ns_conf.marshal_with(datasource_metadata)
    def put(self, name):
        '''add new datasource'''
        datasource = {
            'name': name
            ,'source': api.payload['source']
            ,'created_at': str(datetime.datetime.now())
            ,'update_at': str(datetime.datetime.now())
            ,'row_count': 0
        }
        with open('storage/datasource_{}.json'.format(name), 'w') as fp:
            json.dump(datasource, fp)

        datasource['created_at'] = parse(datasource['created_at'])
        datasource['update_at'] = parse(datasource['update_at'])

        return datasource

@ns_conf.route('/<name>/data/')
@ns_conf.param('name', 'Datasource name')
class DatasourceData(Resource):
    @ns_conf.doc('get_datasource_data', params=get_datasource_rows_params)
    @ns_conf.marshal_with(datasource_rows_metadata)
    def get(self, name):
        '''return data rows'''
        return GET_DATASOURCE_ROWS_EXAMPLES[0]

@ns_conf.route('/<name>/files/<column_name>:<index>')
@ns_conf.param('name', 'Datasource name')
@ns_conf.param('column_name', 'column name')
@ns_conf.param('index', 'row index')
class DatasourceFiles(Resource):
    @ns_conf.doc('put_datasource_file', params=put_datasource_file_params)
    def put(self, name):
        '''put file'''
        return '', 200

@ns_conf.route('/<name>/missed_files')
@ns_conf.param('name', 'Datasource name')
class DatasourceMissedFiles(Resource):
    @ns_conf.doc('get_datasource_missed_files', params=get_datasource_missed_files_params)
    @ns_conf.marshal_with(datasource_missed_files_metadata)
    def get(self, name):
        '''return missed files'''
        return GET_DATASOURCE_MISSED_FILES_EXAMPLES[0]
