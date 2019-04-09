from mindsdb_server.namespaces.configs.predictors import ns_conf
from mindsdb_server.namespaces.entitites.histogram_data import histogram_data
from mindsdb_server.namespaces.entitites.nested_histogram_data import nested_histogram_data

from flask_restplus import fields

target_column_metadata = ns_conf.model('TargetColumnMetadata', {
    'column_name': fields.String(required=True, description='The column name'),
    'overall_input_importance': fields.Nested(histogram_data, required=False, description='The overall predictor feature importance'),
    'train_accuracy_over_time': fields.Nested(histogram_data, required=True, description='The predictor train accuracy over time'),
    'test_accuracy_over_time': fields.Nested(histogram_data, required=True, description='The predictor test accuracy over time'),
    'accuracy_histogram': fields.Nested(nested_histogram_data, required=False, description='The predictor accuracy acrross values'),
})
