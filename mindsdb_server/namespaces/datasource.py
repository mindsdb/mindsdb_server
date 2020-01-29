import datetime
import json
import os
import shutil

import mindsdb
from dateutil.parser import parse
from flask import request, send_file
from flask_restplus import Resource, abort
from mindsdb import FileDS

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

app, api = get_shared()
datasources = []
global_mdb = mindsdb.Predictor(name='datasource_metapredictor')

def get_datasources():
    datasources = []
    for ds_name in os.listdir(mindsdb.CONFIG.MINDSDB_DATASOURCES_PATH):
        try:
            with open(os.path.join(mindsdb.CONFIG.MINDSDB_DATASOURCES_PATH, ds_name, 'metadata.json'), 'r') as fp:
                try:
                    datasource = json.load(fp)
                    datasource['created_at'] = parse(datasource['created_at'].split('.')[0])
                    datasource['updated_at'] = parse(datasource['updated_at'].split('.')[0])
                    datasources.append(datasource)
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)
    return datasources


def get_datasource(name):
    for ds in get_datasources():
        if ds['name'] == name:
            return ds
    return None

def save_datasource_metadata(ds):
        ds['created_at'] = str(ds['created_at']).split('.')[0]
        ds['updated_at'] = str(datetime.datetime.now()).split('.')[0]

        with open(os.path.join(mindsdb.CONFIG.MINDSDB_DATASOURCES_PATH, ds['name'], 'metadata.json'), 'w') as fp:
            json.dump(ds, fp)


@ns_conf.route('/')
class DatasourcesList(Resource):
    @ns_conf.doc('get_datasources_list')
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
        ds = get_datasource(name)
        if ds is not None:
            return ds
        return '', 404

    @ns_conf.doc('delete_datasource')
    def delete(self, name):
        '''delete datasource'''
        try:
            data_sources = get_datasource(name)
            shutil.rmtree(os.path.join(mindsdb.CONFIG.MINDSDB_DATASOURCES_PATH, data_sources['name']))
        except Exception as e:
            print(e)
            abort(400, str(e))
        return '', 200

    @ns_conf.doc('put_datasource', params=put_datasource_params)
    @ns_conf.marshal_with(datasource_metadata)
    def put(self, name):
        '''add new datasource'''
        data = request.json or request.values

        datasource_name = data['name']
        datasource_type = data['source_type']
        datasource_source = data['source']

        if datasource_type == 'file' and 'file' not in request.files:
            abort(400, "Argument 'file' is missing")

        names = [x['name'] for x in get_datasources()]
        print(names)
        for i in range(1, 100):
            if datasource_name in names:
                previous_index = i - 1
                datasource_name = datasource_name.replace(f'({previous_index})', '')
                datasource_name += f'({i})'
            else:
                break

        os.mkdir(os.path.join(mindsdb.CONFIG.MINDSDB_DATASOURCES_PATH, datasource_name))
        os.mkdir(os.path.join(mindsdb.CONFIG.MINDSDB_DATASOURCES_PATH, datasource_name, 'resources'))

        if datasource_type == 'file':
            datasource_file = request.files['file']
            os.mkdir(os.path.join(mindsdb.CONFIG.MINDSDB_DATASOURCES_PATH, datasource_name, 'datasource'))
            datasource_source = str(
                os.path.join(mindsdb.CONFIG.MINDSDB_DATASOURCES_PATH, datasource_name, 'datasource', datasource_source))
            open(datasource_source, 'wb').write(datasource_file.read())
            ds = FileDS(datasource_source)
        else:
            ds = FileDS(datasource_source)

        columns = [dict(name=x) for x in list(ds.df.keys())]
        row_count = len(ds.df)

        new_data_source = {
            'name': datasource_name,
            'source_type': datasource_type,
            'source': datasource_source,
            'missed_files': False,
            'created_at': datetime.datetime.now(),
            'updated_at': datetime.datetime.now(),
            'row_count': row_count,
            'columns': columns
        }

        save_datasource_metadata(new_data_source)

        return get_datasource(datasource_name)


@ns_conf.route('/<name>/analyze')
@ns_conf.param('name', 'Datasource name')
class Analyze(Resource):
    @ns_conf.doc('analyse_dataset')
    def get(self, name):
        global global_mdb
        ds = get_datasource(name)
        if ds['name'] is None:
            print('No valid datasource given')
            abort(400, 'No valid datasource given')

        if 'analysis_data' in ds and ds['analysis_data'] is not None:
            return ds['analysis_data'], 200

        analysis = global_mdb.analyse_dataset(ds['source'], sample_margin_of_error=0.025)

        ds['analysis_data'] = analysis
        save_datasource_metadata(ds)

        return analysis, 200


@ns_conf.route('/<name>/data/')
@ns_conf.param('name', 'Datasource name')
class DatasourceData(Resource):
    @ns_conf.doc('get_datasource_data', params=get_datasource_rows_params)
    @ns_conf.marshal_with(datasource_rows_metadata)
    def get(self, name):
        '''return data rows'''
        ds_record = ([x for x in get_datasources() if x['name'] == name] or [None])[0]
        if ds_record:
            path = ds_record['source']
            if ds_record['source_type'] == 'file':
                if not os.path.exists(path):
                    abort(404, "")
            ds = FileDS(path)
            keys = list(ds.df.keys())
            response = {
                'data': [dict(zip(keys, x)) for x in ds.df.values]
            }
            return response, 200
        abort(404, "")


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
        filesDir = os.path.join(mindsdb.CONFIG.MINDSDB_DATASOURCES_PATH, name, 'files')
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
        abort(404, '')


@ns_conf.route('/<name>/download')
@ns_conf.param('name', 'Datasource name')
class DatasourceMissedFilesDownload(Resource):
    @ns_conf.doc('get_datasource_download')
    def get(self, name):
        '''download uploaded file'''
        ds = get_datasource(name)
        if not ds:
            abort(404, "{} not found".format(name))
        if not os.path.exists(ds['source']):
            abort(404, "{} not found".format(name))

        return send_file(os.path.abspath(ds['source']), as_attachment=True)
