from mindsdb_server.namespaces.configs.predictors import ns_conf
from mindsdb_server.namespaces.entitites.quality_metric import quality_metric
from flask_restplus import fields

quality_dimension = ns_conf.model('QualityDimension', {
    'score': fields.String(required=True, description='The score fraction representation X/Y, which can be evaluated on front end if need be'),
    'metrics': fields.List(fields.Nested(quality_metric), required=False, description='List of quality metrics evaluated'),
    'description': fields.String(required=True, description='The score description')
})