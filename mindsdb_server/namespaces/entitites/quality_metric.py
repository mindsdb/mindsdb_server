from mindsdb_server.namespaces.configs.predictors import ns_conf
from flask_restplus import fields


quality_metric = ns_conf.model('QualityMetric', {
    'type': fields.String(required=True, description='The quality type', enum=['error', 'warning', 'info']),
    'score': fields.Float(required=True, description='The score on the specific metric value 0-1'),
    'description': fields.String(required=True, description='The quality metric description')
})