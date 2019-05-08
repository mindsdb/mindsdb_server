import os
import time
import datetime
from flask import request, send_file
from flask_restplus import Resource, fields

from mindsdb.libs.data_sources.file_ds import FileDS

from mindsdb_server.namespaces.configs.datasources import ns_conf
from mindsdb_server.namespaces.entitites.datasources.datasource import (
    datasource_metadata,
    put_datasource_params
)
from mindsdb_server.namespaces.entitites.datasources.datasource_data import (
    get_datasource_rows_params,
    datasource_rows_metadata
)
from mindsdb_server.namespaces.entitites.datasources.datasource_files import (
    put_datasource_file_params
)
from mindsdb_server.namespaces.entitites.datasources.datasource_missed_files import (
    datasource_missed_files_metadata,
    get_datasource_missed_files_params
)

from mindsdb_server.shared_ressources import get_shared
import json
import datetime
from dateutil.parser import parse
import os
import shutil

app, api = get_shared()
datasources = []


def get_datasources():
    datasources = []
    for ds_name in os.listdir('storage'):
        with open(os.path.join('storage', ds_name, 'metadata.json'), 'r') as fp:
            try:
                datasource = json.load(fp)
                datasource['created_at'] = parse(datasource['created_at'].split('.')[0])
                datasource['updated_at'] = parse(datasource['updated_at'].split('.')[0])
                datasources.append(datasource)
            except Exception as e:
                print(e)
    return datasources

def get_datasource(name):
    for ds in get_datasources():
        if ds['name'] == name:
            return ds
    return None


@ns_conf.route('/')
class DatasourcesList(Resource):
    @ns_conf.doc('get_atasources_list')
    @ns_conf.marshal_list_with(datasource_metadata)
    def get(self):
        '''List all datasources'''
        return get_datasources()

@ns_conf.route('/<name>')
@ns_conf.param('name', 'Datasource name')
class Datasource(Resource):
    @ns_conf.doc('get_datasource')
    @ns_conf.marshal_with(datasource_metadata)
    def get(self, name):
        '''return datasource metadata'''
        ds = get_datasource()
        if ds is not None:
            return ds
        return '', 404

    @ns_conf.doc('delete_datasource')
    def delete(self, name):
        '''delete datasource'''
        try:
            data_sources = get_datasource(name)
            shutil.rmtree(os.path.join('storage', data_sources['name']))
        except Exception as e:
            print(e)
            return str(e), 400
        return '', 200

    @ns_conf.doc('put_datasource', params=put_datasource_params)
    @ns_conf.marshal_with(datasource_metadata)
    def put(self, name):
        '''add new datasource'''
        data = request.json or request.values

        datasource_name = data['name']
        datasource_type = data['source_type']
        datasource_source = data['source']

        names = [x['name'] for x in get_datasources()]
        if datasource_name in names:
            datasource_name += '(1)'

        os.mkdir(os.path.join('storage', datasource_name))
        os.mkdir(os.path.join('storage', datasource_name, 'resources'))

        if datasource_type == 'file':
            datasource_file = request.files['file']
            os.mkdir(os.path.join('storage', datasource_name, 'datasource'))
            path = os.path.join('storage', datasource_name, 'datasource', datasource_source)
            open(path, 'wb').write(datasource_file.read())
            ds = FileDS(path)
        else:
            ds = FileDS(datasource_source)

        columns = [dict(name=x) for x in list(ds.df.keys())]
        row_count = len(ds.df)

        new_data_source = {
            'name': datasource_name,
            'source_type': datasource_type,
            'source': datasource_source,
            'missed_files': False,
            'created_at': str(datetime.datetime.now()).split('.')[0],
            'updated_at': str(datetime.datetime.now()).split('.')[0],
            'row_count': row_count,
            'columns': columns
        }

        with open(os.path.join('storage', datasource_name, 'metadata.json'), 'w') as fp:
            json.dump(new_data_source, fp)

        return get_datasource(datasource_name)

@ns_conf.route('/<name>/data/')
@ns_conf.param('name', 'Datasource name')
class DatasourceData(Resource):
    @ns_conf.doc('get_datasource_data', params=get_datasource_rows_params)
    @ns_conf.marshal_with(datasource_rows_metadata)
    def get(self, name):
        '''return data rows'''
        ds_record = ([x for x in get_datasources() if x['name'] == name] or [None])[0]
        if ds_record:
            if ds_record['source_type'] == 'file':
                path = os.path.join('storage', ds_record['source'])
                if not os.path.exists(path):
                    return '', 404
            else:
                path = ds_record['source']
            ds = FileDS(path)
            keys = list(ds.df.keys())
            response = {
                'data': [dict(zip(keys,x)) for x in ds.df.values]
            }
            return response, 200
        return '', 404

@ns_conf.route('/<name>/files/<column_name>:<index>')
@ns_conf.param('name', 'Datasource name')
@ns_conf.param('column_name', 'column name')
@ns_conf.param('index', 'row index')
class DatasourceFiles(Resource):
    @ns_conf.doc('put_datasource_file', params=put_datasource_file_params)
    def put(self, name, column_name, index):
        '''put file'''
        extension = request.values['extension']
        fileName = '{}-{}{}'.format(column_name, index, extension)
        file = request.files['file']
        filesDir = os.path.join('storage', name, 'files')
        filePath = os.path.join(filesDir, fileName)

        if not os.path.exists(filesDir):
            os.makedirs(filesDir)

        open(filePath, 'wb').write(file.read())
        return '', 200

@ns_conf.route('/<name>/missed_files')
@ns_conf.param('name', 'Datasource name')
class DatasourceMissedFiles(Resource):
    @ns_conf.doc('get_datasource_missed_files', params=get_datasource_missed_files_params)
    @ns_conf.marshal_with(datasource_missed_files_metadata)
    def get(self, name):
        '''return missed files'''
        return '', 404


@ns_conf.route('/<name>/download')
@ns_conf.param('name', 'Datasource name')
class DatasourceMissedFiles(Resource):
    @ns_conf.doc('get_datasource_download')
    def get(self, name):
        '''download uploaded file'''
        ds = ([x for x in get_datasources() if x['name'] == name] or [None])[0]
        if not ds:
            return '', 404
        path = os.path.join('storage', ds['source'])
        if not os.path.exists(path):
            return '', 404

        return send_file(path, as_attachment=True)
