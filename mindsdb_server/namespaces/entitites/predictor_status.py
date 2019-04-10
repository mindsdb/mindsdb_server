from mindsdb_server.namespaces.configs.predictors import ns_conf

from flask_restplus import fields
import datetime

predictor_status = ns_conf.model('PredictorStatus', {
    # Primary key
    'name': fields.String(required=True, description='The predictor name, NOTE: That primary key is made of name:version'),
    'version': fields.String(required=True, description='The predictor version to publish under, this is so that we can train multiple predictors for the same problem but expose them via the same name'),
    # other attributes
    'is_active': fields.Boolean(required=True, description='Only one predictor by public_name can be active'),
    'data_source': fields.String(required=True, description='The data source it\'s learning from'),
    'predict': fields.List(fields.String, required=True, description='The list of columns/fields to be predicted'),
    'accuracy': fields.Float(description='The current accuracy of the model'),
    'status': fields.String(required=True, description='The current model status', enum=['training', 'complete']),
    'train_end_at': fields.DateTime(description='The time the predictor finished training'),
    'updated_at': fields.DateTime(required=True, description='The time the predictor was last updated at'),
    'created_at': fields.DateTime(required=True, description='The time the predictor was created at')
})




##EXAMPLES



EXAMPLES = [
    {
        'name': 'Price',
        'version': 1,
        'is_active': True,
        'data_source': 'real_estate.csv',
        'predict': ['price'],
        'accuracy': '.97',
        'status': 'training',
        'train_end_at': datetime.datetime.now(),
        'updated_at': datetime.datetime.now(),
        'created_at': datetime.datetime.now()
    },
    {
        'name': 'Price',
        'version': 2,
        'is_active': False,
        'data_source': 'real_estate_complex.csv',
        'predict': ['price'],
        'accuracy': '.64',
        'status': 'training',
        'train_end_at': datetime.datetime.now(),
        'updated_at': datetime.datetime.now(),
        'created_at': datetime.datetime.now()
    },
    {
        'name': 'Number of rooms',
        'version': 1,
        'is_active': True,
        'data_source': 'real_estate.csv',
        'predict': ['number_of_rooms'],
        'accuracy': '.97',
        'status': 'complete',
        'train_end_at': datetime.datetime.now(),
        'updated_at': datetime.datetime.now(),
        'created_at': datetime.datetime.now()
    }
]