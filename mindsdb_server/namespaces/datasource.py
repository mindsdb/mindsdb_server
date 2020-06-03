import datetime
import json
import os
import shutil
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

def create_sqlite_db(path, data_frame):
    con = sqlite3.connect(path)
    data_frame.to_sql(name='data', con=con, index=False)
    con.close()

def get_analysis(source):
    global global_mdb
    return global_mdb.analyse_dataset(source, sample_margin_of_error=0.025)

def cast_df_columns_types(df):
    types_map = {
        DATA_TYPES.NUMERIC: {
            DATA_SUBTYPES.INT: 'int64',
            DATA_SUBTYPES.FLOAT: 'float64',
            DATA_SUBTYPES.BINARY: 'bool'
        },
        DATA_TYPES.DATE: {
            DATA_SUBTYPES.DATE: 'datetime64',       # YYYY-MM-DD
            DATA_SUBTYPES.TIMESTAMP: 'datetime64'   # YYYY-MM-DD hh:mm:ss or 1852362464
        },
        DATA_TYPES.CATEGORICAL: {
            DATA_SUBTYPES.SINGLE: 'category',
            DATA_SUBTYPES.MULTIPLE: 'category'
        },
        DATA_TYPES.FILE_PATH: {
            DATA_SUBTYPES.IMAGE: 'object',
            DATA_SUBTYPES.VIDEO: 'object',
            DATA_SUBTYPES.AUDIO: 'object'
        },
        DATA_TYPES.SEQUENTIAL: {
            DATA_SUBTYPES.TEXT: 'object',
            DATA_SUBTYPES.ARRAY: 'object'
        }
    }

    analysis = get_analysis(df)
    columns = [dict(name=x) for x in list(df.keys())]

    for column in columns:
        try:
            name = column['name']
            col_type = analysis['data_analysis_v2'][name]['typing']['data_type']
            col_subtype = analysis['data_analysis_v2'][name]['typing']['data_subtype']
            new_type = types_map[col_type][col_subtype]
            if new_type == 'int64' or new_type == 'float64':
                df[name] = df[name].apply(lambda x: x.replace(',','.'))
            if new_type == 'int64':
                df = df.astype({name: 'float64'})
            df = df.astype({name: new_type})
        except Exception as e:
            print(e)
            print(f'Error: cant convert type of DS column {name} to {new_type}')
    
    return df

def parse_filter(key, value):
    result = re.search(r'filter(_*.*)\[(.*)\]', key)
    operator = result.groups()[0].strip('_') or 'like'
    field = result.groups()[1]
    operators_map = {
        'like': 'like',
        'in': 'in',
        'nin': 'not in',
        'gt': '>',
        'lt': '<',
        'gte': '>=',
        'lte': '<=',
        'eq': '=',
        'neq': '!='
    }
    if operator not in operators_map:
        return None
    operator = operators_map[operator]
    return {'field': field, 'value': value, 'operator': operator}


def prepare_sql_where(where):
    marks = {}
    if len(where) > 0:
        for i in range(len(where)):
            field = where[i]['field'].replace('"', '""')
            operator = where[i]['operator']
            value = where[i]['value']
            var_name = f'var{i}'
            if ' ' in field:
                field = f'"{field}"'
            if operator == 'like':
                marks[var_name] = '%' + value + '%'
            else:
                marks[var_name] = value
            where[i] = f'{field} {operator} :var{i}'
        where = 'where ' + ' and '.join(where)
    else:
        where = ''
    return where, marks

def get_sqlite_columns_names(cursor):
    cursor.execute('pragma table_info(data);')
    column_name_index = [x[0] for x in cursor.description].index('name')
    columns = cursor.fetchall()
    return [x[column_name_index] for x in columns]

def get_sqlite_data(db_path, where=[], limit=None, offset=None):
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    offset = '' if limit is None or offset is None else f'offset {offset}'
    limit = '' if limit is None else f'limit {limit}'

    columns_names = get_sqlite_columns_names(cur)
    where = [x for x in where if x['field'] in columns_names]
    where, marks = prepare_sql_where(where)

    count_query = ' '.join(['select count(1) from data', where])
    cur.execute(count_query, marks)
    rowcount = cur.fetchone()[0]

    query = ' '.join(['select * from data', where, limit, offset])
    cur.execute(query, marks)
    data = cur.fetchall()
    data = [dict(zip(columns_names, x)) for x in data]

    cur.close()
    con.close()

    return {
        'data': data,
        'rowcount': rowcount,
        'columns_names': columns_names
    }


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
        data = {}
        def on_field(field):
            name = field.field_name.decode()
            value = field.value.decode()
            data[name] = value

        def on_file(file):
            data['file'] = file.file_name.decode()

        temp_dir_path = tempfile.mkdtemp(prefix='gateway_')

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

        if 'name' in data:
            datasource_name = data['name']
        else:
            datasource_name = name
        datasource_type = data['source_type']

        if 'source' in data:
            datasource_source = data['source']
        else:
            datasource_source = name

        if datasource_type == 'file' and 'file' not in data:
            abort(400, "Argument 'file' is missing")

        names = [x['name'] for x in get_datasources()]

        for i in range(1, 100):
            if datasource_name in names:
                previous_index = i - 1
                datasource_name = datasource_name.replace(f'({previous_index})', '')
                datasource_name += f'({i})'
            else:
                break

        os.mkdir(os.path.join(mindsdb.CONFIG.MINDSDB_DATASOURCES_PATH, datasource_name))
        os.mkdir(os.path.join(mindsdb.CONFIG.MINDSDB_DATASOURCES_PATH, datasource_name, 'resources'))

        ds_dir = os.path.join(mindsdb.CONFIG.MINDSDB_DATASOURCES_PATH, datasource_name, 'datasource')
        os.mkdir(ds_dir)
        if datasource_type == 'file':
            datasource_source = os.path.join(mindsdb.CONFIG.MINDSDB_DATASOURCES_PATH, datasource_name, 'datasource', datasource_source)
            os.replace(
                os.path.join(temp_dir_path, data['file']),
                datasource_source
            )
            ds = FileDS(datasource_source)
        else:
            ds = FileDS(datasource_source)

        os.rmdir(temp_dir_path)

        df = ds.df
        columns = [dict(name=x) for x in list(df.keys())]
        row_count = len(df)

        df_with_types = cast_df_columns_types(df)
        create_sqlite_db(os.path.join(ds_dir, 'sqlite.db'), df_with_types)

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
        global global_mdb
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
