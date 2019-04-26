from io import BytesIO
from flask import request, send_file
from flask_restplus import Resource, fields

from mindsdb_server.namespaces.entitites.predictor_status import predictor_status, EXAMPLES as PREDICTORS_STATUS_LIST
from mindsdb_server.namespaces.entitites.predictor_metadata import (
    predictor_metadata,
    predictor_query_params,
    EXAMPLES as PREDICTOR_METADATA
)
from mindsdb_server.namespaces.configs.predictors import ns_conf
from mindsdb_server.namespaces.entitites.datasources.datasource import EXAMPLES as DATASOURCES_LIST_EXAMPLE

import mindsdb

import os
import json
import pickle
import sys
import copy
import numpy
from dateutil.parser import parse as parse_datetime

FILES_PATH = 'uploads'
from multiprocessing import Process


# Temporary maping for testing
    # key - predictor name
    # value - datasource name
DTASOURCE_PREDICTOR_MAP = {
}


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

@ns_conf.route('/')
class PredictorList(Resource):
    @ns_conf.doc('list_predictors')
    @ns_conf.marshal_list_with(predictor_status, skip_none=True)
    def get(self):
        '''List all predictors'''

        mdb = mindsdb.Predictor(name='metapredictor')
        models = mdb.get_models()

        for model in models:
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
        '''View predictor statistics'''
        # return PREDICTOR_METADATA[0]
        mdb = mindsdb.Predictor(name=name)
        model = mdb.get_model_data(name)

        for k in ['train_end_at', 'updated_at', 'created_at']:
            if k in model:
                model[k] = parse_datetime(model[k])

        #debug_pkey_type(model)
        #print(model['data_analysis']['target_columns_metadata'])
        #model['data_analysis']['target_columns_metadata'] = 0
        #model['data_analysis']['input_columns_metadata'] = 0

        return model

    @ns_conf.doc('delete_predictor')
    def delete(self, name):
        '''Remove predictor'''
        return '', 200

    @ns_conf.doc('get_predictor')
    def put(self, name):
        '''Learning new predictor'''
        data = request.json
        from_data = data.get('from_data')
        to_predict = data.get('to_predict')

        if data.get('data_source_name'):
            DTASOURCE_PREDICTOR_MAP[name] = data.get('data_source_name')
            ds = ([x for x in DATASOURCES_LIST_EXAMPLE if x['name'] == data.get('data_source_name')] or [None])[0]
            if ds and ds['source']:
                if ds['source_type'] == 'url':
                    from_data = ds['source']
                if ds['source_type'] == 'file':
                    from_data = os.path.join(FILES_PATH, ds['source'])

        if not name or not from_data or not to_predict:
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

        p = Process(target=learn, args=(name, from_data, to_predict))
        p.start()

        return '', 200

        # mdb = mindsdb.Predictor(name=name)
        # model = mdb.get_model_data(name)
        # for k in ['train_end_at', 'updated_at', 'created_at']:
        #     if k in model:
        #         model[k] = parse_datetime(model[k])
        # return model


@ns_conf.route('/<name>/columns')
@ns_conf.param('name', 'The predictor identifier')
class PredictorColumns(Resource):
    @ns_conf.doc('get_predictor_columns')
    def get(self, name):
        '''List of predictors colums'''
        # temporary defaults for testing
        DEFAULT_COLUMNS = [
            { 'name': 'location', 'type': 'string' },
            { 'name': 'rental_price', 'type': 'number' },
        ]
        ds_name = DTASOURCE_PREDICTOR_MAP.get(name)
        columns = DEFAULT_COLUMNS
        if ds_name:
            ds = ([x for x in DATASOURCES_LIST_EXAMPLE if x['name'] == ds_name] or [None])[0]
            if ds:
               columns = ds['columns']

        return columns, 200


@ns_conf.route('/<name>/predict')
@ns_conf.param('name', 'The predictor identifier')
class PredictorPredict(Resource):
    @ns_conf.doc('post_predictor_predict', params=predictor_query_params)
    def post(self, name):
        '''Queries predictor'''
        when = request.json.get('when') or {}
        mdb = mindsdb.Predictor(name=name)
        result = mdb.predict(when=when)
        if result and len(result):
            response = result[0].as_dict()
            response = dict([(key, float(val)) if isinstance(val, numpy.float32) else (key, val) for key, val in response.items()])
            return response
        return '', 400


@ns_conf.route('/<name>/upload')
@ns_conf.param('name', 'The predictor identifier')
class PredictorUpload(Resource):
    @ns_conf.doc('predictor_query')
    def put(self, name):
        '''Upload existing predictor'''
        predictor_file = request.files['file']
        predictor_file.read()
        return '', 200


@ns_conf.route('/<name>/download')
@ns_conf.param('name', 'The predictor identifier')
class PredictorDownload(Resource):
    @ns_conf.doc('get_predictor_download')
    def get(self, name):
        '''Export predictor to file'''
        return send_file(BytesIO(b'this is mocked data'), mimetype='text/plain', attachment_filename='predictor_export_mock.txt', as_attachment=True)
