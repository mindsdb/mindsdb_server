from flask import request
from flask_restplus import Resource, fields

from mindsdb_server.namespaces.entitites.predictor_status import predictor_status, EXAMPLES as PREDICTORS_STATUS_LIST
from mindsdb_server.namespaces.entitites.predictor_metadata import predictor_metadata, EXAMPLES as PREDICTOR_METADATA
from mindsdb_server.namespaces.configs.predictors import ns_conf
from mindsdb_server.namespaces.entitites.datasources.datasource import EXAMPLES as DATASOURCES_LIST_EXAMPLE

import mindsdb

import os
import json
import pickle
import sys
import copy
from dateutil.parser import parse as parse_datetime

FILES_PATH = 'uploads'
from multiprocessing import Process


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
        # return PREDICTOR_METADATA[0]
        mdb = mindsdb.Predictor(name='metapredictor')
        model = mdb.get_model_data(name)

        for k in ['train_end_at', 'updated_at', 'created_at']:
            if k in model:
                model[k] = parse_datetime(model[k])

        #debug_pkey_type(model)
        #print(model['data_analysis']['target_columns_metadata'])
        #model['data_analysis']['target_columns_metadata'] = 0
        #model['data_analysis']['input_columns_metadata'] = 0

        return model

    @ns_conf.doc('get_predictor')
    def put(self, name):
        '''learning new predictor'''
        data = request.json
        from_data = data.get('from_data')
        to_predict = data.get('to_predict')

        if data.get('data_source_name'):
            ds = ([x for x in DATASOURCES_LIST_EXAMPLE if x['name'] == name] or [None])[0]
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

        mdb = mindsdb.Predictor(name=name)
        model = mdb.get_model_data(name)
        for k in ['train_end_at', 'updated_at', 'created_at']:
            if k in model:
                model[k] = parse_datetime(model[k])
        return model

