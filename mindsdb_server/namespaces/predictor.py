from flask_restplus import Resource, fields

from mindsdb_server.namespaces.entitites.predictor_status import predictor_status, EXAMPLES as PREDICTORS_STATUS_LIST
from mindsdb_server.namespaces.entitites.predictor_metadata import predictor_metadata, EXAMPLES as PREDICTOR_METADATA

from mindsdb_server.namespaces.configs.predictors import ns_conf
import json
import pickle
import sys
import mindsdb
from dateutil.parser import parse as parse_datetime


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
        mdb = mindsdb.Predictor(name='metapredictor')
        model = mdb.get_model_data(name)

        for k in ['train_end_at', 'updated_at', 'created_at']:
            if k in model:
                model[k] = parse_datetime(model[k])

        return model
