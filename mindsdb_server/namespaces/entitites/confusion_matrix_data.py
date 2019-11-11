from mindsdb_server.namespaces.configs.predictors import ns_conf
from mindsdb_server.namespaces.entitites.column_metadata import column_metadata

from flask_restplus import fields

confusion_matrix_data = ns_conf.model('ConfusionMatrixData', {
    'matrix': fields.List(fields.List(fields.Integer, required=True)),
    'predicted': fields.List(fields.String, required=False, description='Predicted values'),
    'real': fields.List(fields.String, required=False, description='Real values'),
})
