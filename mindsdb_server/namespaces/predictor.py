from flask_restplus import Resource, fields

from mindsdb_server.namespaces.entitites.predictor_status import predictor_status, EXAMPLES as PREDICTORS_STATUS_LIST
from mindsdb_server.namespaces.entitites.predictor_metadata import predictor_metadata, EXAMPLES as PREDICTOR_METADATA
from mindsdb_server.namespaces.configs.predictors import ns_conf
from mindsdb_server.shared_ressources import get_shared
from mindsdb_server.namespaces.datasource import get_datasource
import mindsdb

import json
import pickle
import sys
import copy
from dateutil.parser import parse as parse_datetime


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

@ns_conf.route('/')
class PredictorList(Resource):
    @ns_conf.doc('list_predictors')
    @ns_conf.marshal_list_with(predictor_status, skip_none=True)
    def get(self):
        '''List all predictors'''

        mdb = mindsdb.Predictor(name='metapredictor', root_folder='~/mindsdb/mindsdb_storage/1_0_7')
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
        mdb = mindsdb.Predictor(name='metapredictor', root_folder='~/mindsdb/mindsdb_storage/1_0_7')
        model = mdb.get_model_data(name)

        for k in ['train_end_at', 'updated_at', 'created_at']:
            if k in model:
                model[k] = parse_datetime(model[k])

        return model

    def put(self, name):
        '''Train a predictor'''
        mdb = mindsdb.Predictor(name=name)

        datasource = None
        for ds in get_datasource:
            if ds.name == api.payload.data_source:
                datasource = ds

        if 'http://' in datasource.source or 'https://' in datasource.source:
            mdb.learn(from_data=datasource.source, to_predict=[api.payload.predicted_fields])
        else:
            mdb.learn(from_data= 'storage/datasource_files/' + datasource.source, to_predict=[api.payload.predicted_fields])
