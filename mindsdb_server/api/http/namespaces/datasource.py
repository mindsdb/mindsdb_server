import datetime
import json
import os
import sqlite3
import re

import tempfile
import multipart
import csv

import mindsdb
from dateutil.parser import parse
from flask import request, send_file
from flask_restx import Resource, abort
from mindsdb import FileDS
from mindsdb.libs.constants.mindsdb import DATA_TYPES, DATA_SUBTYPES

from mindsdb_server.api.http.namespaces.configs.datasources import ns_conf
from mindsdb_server.api.http.namespaces.entitites.datasources.datasource import (
    datasource_metadata,
    put_datasource_params
)
from mindsdb_server.api.http.namespaces.entitites.datasources.datasource_data import (
    get_datasource_rows_params,
    datasource_rows_metadata
)
from mindsdb_server.api.http.namespaces.entitites.datasources.datasource_files import (
    put_datasource_file_params
)
from mindsdb_server.api.http.namespaces.entitites.datasources.datasource_missed_files import (
    datasource_missed_files_metadata,
    get_datasource_missed_files_params
)
from mindsdb_server.api.http.shared_ressources import get_shared
from mindsdb_server.interfaces.datastore.datastore import DataStore

app, api = get_shared()
datasources = []
default_store = DataStore('/home/george/fucking_around/store')

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
        ds = default_store.get_datasource(name)
        if ds is not None:
            return ds
        return '', 404

    @ns_conf.doc('delete_datasource')
    def delete(self, name):
        '''delete datasource'''
        try:
            default_store.delete_datasource(name)
        except Exception as e:
            print(e)
            abort(400, str(e))
        return '', 200

    @ns_conf.doc('put_datasource', params=put_datasource_params)
    @ns_conf.marshal_with(datasource_metadata)
    def put(self, name):
        '''add new datasource'''
        data = {}
        def on_field(field):
            name = field.field_name.decode()
            value = field.value.decode()
            data[name] = value

        def on_file(file):
            data['file'] = file.file_name.decode()

        temp_dir_path = tempfile.mkdtemp(prefix='datasource_file_')

        parser = multipart.create_form_parser(
            headers=request.headers,
            on_field=on_field,
            on_file=on_file,
            config={
                'UPLOAD_DIR': temp_dir_path.encode(),    # bytes required
                'UPLOAD_KEEP_FILENAME': True,
                'UPLOAD_KEEP_EXTENSIONS': True,
                'MAX_MEMORY_FILE_SIZE': 0
            }
        )

        while True:
            chunk = request.stream.read(8192)
            if not chunk:
                break
            parser.write(chunk)
        parser.finalize()
        parser.close()

        ds_name = data['name'] if 'name' in data else name
        source = data['source'] if 'source' in data else name
        source_type = data['source_type']

        if datasource_type == 'file':
            file_path = os.path.join(temp_dir_path, data['file'])
        else:
            file_path = None

        default_store.save_datasource(ds_name, source_type, source, file_path)
        os.rmdir(temp_dir_path)

        return get_datasource(datasource_name)


@ns_conf.route('/<name>/analyze')
@ns_conf.param('name', 'Datasource name')
class Analyze(Resource):
    @ns_conf.doc('analyse_dataset')
    def get(self, name):
        ds = get_datasource(name)
        if ds is None:
            print('No valid datasource given')
            abort(400, 'No valid datasource given')

        if 'analysis_data' in ds and ds['analysis_data'] is not None:
            return ds['analysis_data'], 200

        analysis = get_analysis(ds['source'])

        ds['analysis_data'] = analysis
        save_datasource_metadata(ds)

        return analysis, 200


@ns_conf.route('/<name>/analyze_subset')
@ns_conf.param('name', 'Datasource name')
class AnalyzeSubset(Resource):
    @ns_conf.doc('analyse_datasubset')
    def get(self, name):
        ds = get_datasource(name)
        if ds is None:
            print('No valid datasource given')
            abort(400, 'No valid datasource given')

        ds_dir = os.path.join(mindsdb.CONFIG.MINDSDB_DATASOURCES_PATH, ds['name'], 'datasource')
        db_path = os.path.join(ds_dir, 'sqlite.db')

        where = []
        for key, value in request.args.items():
            if key.startswith('filter'):
                param = parse_filter(key, value)
                if param is None:
                    abort(400, f'Not valid filter "{key}"')
                where.append(param)

        sqlite_data = get_sqlite_data(db_path, where)

        if sqlite_data['rowcount'] == 0:
            return abort(400, 'Empty dataset after filters applying')

        temp_file_fd, temp_file_path = tempfile.mkstemp(prefix='mindsdb_data_subset_', suffix='.csv', dir='/tmp')
        with open(temp_file_path, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=sqlite_data['columns_names'])
            writer.writeheader()
            for row in sqlite_data['data']:
                writer.writerow(row)

        analysis = get_analysis(temp_file_path)

        os.remove(temp_file_path)

        return analysis, 200


@ns_conf.route('/<name>/data/')
@ns_conf.param('name', 'Datasource name')
class DatasourceData(Resource):
    @ns_conf.doc('get_datasource_data', params=get_datasource_rows_params)
    @ns_conf.marshal_with(datasource_rows_metadata)
    def get(self, name):
        '''return data rows'''
        ds = get_datasource(name)
        if ds is None:
            print('No valid datasource given')
            abort(400, 'No valid datasource given')

        ds_dir = os.path.join(mindsdb.CONFIG.MINDSDB_DATASOURCES_PATH, ds['name'], 'datasource')
        db_path = os.path.join(ds_dir, 'sqlite.db')
        if os.path.isfile(db_path) is False:
            path = ds['source']
            if ds['source_type'] == 'file':
                if not os.path.exists(path):
                    abort(404, "")
            ds = FileDS(path)

            df_with_types = cast_df_columns_types(ds.df)
            create_sqlite_db(os.path.join(ds_dir, 'sqlite.db'), df_with_types)

        params = {
            'page[size]': None,
            'page[offset]': None
        }
        where = []
        for key, value in request.args.items():
            if key == 'page[size]':
                params['page[size]'] = int(value)
            if key == 'page[offset]':
                params['page[offset]'] = int(value)
            elif key.startswith('filter'):
                param = parse_filter(key, value)
                if param is None:
                    abort(400, f'Not valid filter "{key}"')
                where.append(param)

        sqlite_data = get_sqlite_data(db_path, where, params['page[size]'], params['page[offset]'])

        response = {
            'rowcount': sqlite_data['rowcount'],
            'data': sqlite_data['data']
        }
        return response, 200


@ns_conf.route('/<name>/download')
@ns_conf.param('name', 'Datasource name')
class DatasourceMissedFilesDownload(Resource):
    @ns_conf.doc('get_datasource_download')
    def get(self, name):
        '''download uploaded file'''
        ds = default_store.get_datasource(name)
        if not ds:
            abort(404, "{} not found".format(name))
        if not os.path.exists(ds['source']):
            abort(404, "{} not found".format(name))

        return send_file(os.path.abspath(ds['source']), as_attachment=True)
