from flask_restplus import Resource, fields

from mindsdb_server.namespaces.entitites.predictor_status import predictor_status, EXAMPLES as PREDICTORS_STATUS_LIST
from mindsdb_server.namespaces.entitites.predictor_metadata import predictor_metadata, EXAMPLES as PREDICTOR_METADATA

from mindsdb_server.namespaces.configs.predictors import ns_conf
import json
import pickle
import sys

@ns_conf.route('/')
class PredictorList(Resource):
    @ns_conf.doc('list_predictors')
    @ns_conf.marshal_list_with(predictor_status, skip_none=True)
    def get(self):
        '''List all predictors'''

        predictors_list = []
        for fname in [''test_lmd.pickle'']
            with open(fname, 'rb') as fp:
                pdata = pickle.load(fp)

            predictors_list.append({
                    'name': pdata['model_name'],
                    'version': None,
                    'is_active': None,
                    'data_source': pdata['from_data'],
                    'predict': pdata['predict_columns'],
                    'accuracy': None,
                    'status': None,
                    'train_end_at': None,
                    'updated_at': None,
                    'created_at': None
            })
        return predictors_list


@ns_conf.route('/<name>')
@ns_conf.param('name', 'The predictor identifier')
@ns_conf.response(404, 'predictor not found')
class Predictor(Resource):
    @ns_conf.doc('get_predictor')
    @ns_conf.marshal_with(predictor_metadata, skip_none=True)
    def get(self, name):
        '''Fetch a predictor given its identifier'''
        return PREDICTOR_METADATA[0]
