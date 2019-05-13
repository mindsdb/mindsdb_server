from io import BytesIO
from flask import request, send_file
from flask_restplus import Resource, fields

from mindsdb_server.namespaces.entitites.predictor_status import predictor_status
from mindsdb_server.namespaces.entitites.predictor_metadata import (
    predictor_metadata,
    predictor_query_params
)
from mindsdb_server.namespaces.configs.predictors import ns_conf
from mindsdb_server.shared_ressources import get_shared
from mindsdb_server.namespaces.datasource import get_datasource, get_datasources
import mindsdb

import os
import json
import pickle
import sys
import copy
import numpy
import shutil
from dateutil.parser import parse as parse_datetime

from multiprocessing import Process


app, api = get_shared()

def debug_pkey_type(model, keys=None, reset_keyes=True, type_to_check=list, append_key=True):
    if type(model) != dict:
        return
    for k in model:
        if reset_keyes:
            keys = []
        if type(model[k]) == dict:
            keys.append(k)
            debug_pkey_type(model[k], copy.deepcopy(keys), reset_keyes=False)
        if type(model[k]) == type_to_check:
            print(f'They key {keys}->{k} has type list')
        if type(model[k]) == list:
            for item in model[k]:
                debug_pkey_type(item, copy.deepcopy(keys), reset_keyes=False)

def preparse_results(results):
    response_arr = []
    for result in results:
        response = dict(
            [(key, float(val)) if isinstance(val, numpy.float32) else (key, val) for key, val in result.items()]
        )
        response_arr.append(response)
    if len(response_arr) == 1:
        return response_arr[0]
    elif len(response_arr) > 1:
        return response_arr
    else:
        return '', 400

def get_datasource_path(data_source_name):
    if data_source_name:
        ds = get_datasource(data_source_name)
        if ds and ds['source']:
            if ds['source_type'] == 'url':
                return ds['source']
            if ds['source_type'] == 'file':
                return os.path.normpath(os.path.abspath(ds['source']))
    return None

@ns_conf.route('/')
class PredictorList(Resource):
    @ns_conf.doc('list_predictors')
    @ns_conf.marshal_list_with(predictor_status, skip_none=True)
    def get(self):
        '''List all predictors'''

        mdb = mindsdb.Predictor(name='metapredictor')
        models = mdb.get_models()

        for model in models:
            model['data_source'] = model['data_source'].split('/')[-1]
            for k in ['train_end_at', 'updated_at', 'created_at']:
                if k in model:
                    model[k] = parse_datetime(model[k])

        return models


@ns_conf.route('/<name>')
@ns_conf.param('name', 'The predictor identifier')
@ns_conf.response(404, 'predictor not found')
class Predictor(Resource):
    @ns_conf.doc('get_predictor')
    @ns_conf.marshal_with(predictor_metadata, skip_none=True)
    def get(self, name):
        mdb = mindsdb.Predictor(name='metapredictor')
        model = mdb.get_model_data(name)

        for k in ['train_end_at', 'updated_at', 'created_at']:
            if k in model:
                model[k] = parse_datetime(model[k])

        return model

    @ns_conf.doc('delete_predictor')
    def delete(self, name):
        '''Remove predictor'''
        return '', 200

    @ns_conf.doc('put_predictor')
    def put(self, name):
        '''Learning new predictor'''
        data = request.json
        to_predict = data.get('to_predict')

        from_data = get_datasource_path(data.get('data_source_name'))
        if from_data is None:
            from_data = data.get('from_data')
        if from_data is None:
            return 'No valid datasource given', 400

        if name is None or to_predict is None:
            return '', 400

        def learn(name, from_data, to_predict):
            '''
            running at subprocess due to
            ValueError: signal only works in main thread

            this is work for celery worker here?
            '''
            import mindsdb
            mdb = mindsdb.Predictor(name=name)
            mdb.learn(
                from_data=from_data,
                to_predict=to_predict
            )

        print(from_data)
        p = Process(target=learn, args=(name, from_data, to_predict))
        p.start()

        return '', 200

@ns_conf.route('/<name>/columns')
@ns_conf.param('name', 'The predictor identifier')
class PredictorColumns(Resource):
    @ns_conf.doc('get_predictor_columns')
    def get(self, name):
        '''List of predictors colums'''
        mdb = mindsdb.Predictor(name='metapredictor')
        model = mdb.get_model_data(name)

        columns = []
        for col_data in [*model['data_analysis']['target_columns_metadata'], *model['data_analysis']['input_columns_metadata']]:
            columns.append(col_data['column_name'])

        return columns, 200


@ns_conf.route('/<name>/predict')
@ns_conf.param('name', 'The predictor identifier')
class PredictorPredict(Resource):
    @ns_conf.doc('post_predictor_predict', params=predictor_query_params)
    def post(self, name):
        '''Queries predictor'''
        when = request.json.get('when') or {}
        mdb = mindsdb.Predictor(name=name)
        results = mdb.predict(when=when)

        return preparse_results(results)


@ns_conf.route('/<name>/predict_datasource')
@ns_conf.param('name', 'The predictor identifier')
class PredictorPredictFromDataSource(Resource):
    @ns_conf.doc('post_predictor_predict', params=predictor_query_params)
    def post(self, name):
        data = request.json

        from_data = get_datasource_path(data.get('data_source_name'))
        if from_data is None:
            from_data = data.get('from_data')
        if from_data is None:
            from_data = data.get('when_data')
        if from_data is None:
            return 'No valid datasource given', 400

        mdb = mindsdb.Predictor(name=name)
        results = mdb.predict(when_data=from_data)
        return preparse_results(results)

@ns_conf.route('/<name>/upload')
@ns_conf.param('name', 'The predictor identifier')
class PredictorUpload(Resource):
    @ns_conf.doc('predictor_query')
    def put(self, name):
        '''Upload existing predictor'''
        predictor_file = request.files['file']

        fpath = os.path.join('tmp',  name + '.zip')
        with open(fpath, 'wb') as f:
            f.write(predictor_file.read())

        mdb = mindsdb.Predictor(name='metapredictor')
        mdb.load_model(model_archive_path=fpath)
        try:
            os.remove(fpath)
        except Exception:
            pass

        return '', 200


@ns_conf.route('/<name>/download')
@ns_conf.param('name', 'The predictor identifier')
class PredictorDownload(Resource):
    @ns_conf.doc('get_predictor_download')
    def get(self, name):
        '''Export predictor to file'''

        mdb = mindsdb.Predictor(name='metapredictor')
        mdb.export_model(model_name=name)
        fname = name + '.zip'
        fpath = os.path.join('tmp', name + '.zip')
        shutil.move(fname, fpath)

        with open(fpath, 'rb') as f:
            data = BytesIO(f.read())

        try:
            os.remove(fpath)
        except Exception:
            pass

        return send_file(
            data,
            mimetype='application/zip',
            attachment_filename=fname,
            as_attachment=True
        )
