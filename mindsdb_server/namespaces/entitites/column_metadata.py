from mindsdb_server.namespaces.configs.predictors import ns_conf
from mindsdb_server.namespaces.entitites.quality_dimension import quality_dimension
from mindsdb_server.namespaces.entitites.histogram_data import histogram_data, NUMERIC_EXAMPLE
from mindsdb_server.namespaces.entitites.data_distribution_metadata import data_distribution_metadata

from flask_restplus import fields

column_metadata = ns_conf.model('ColumnMetadata', {
    'column_name': fields.String(required=True, description='The column name'),
    'importance_score': fields.Float(required=False, description='This value is given once we have determined the importance score for a given column given the trained model'),
    'data_type': fields.String(required=True, description='The most prevalent data type that we detect', enum=['categorical', 'numeric', 'text', 'image']),
    'data_type_distribution': fields.Nested(histogram_data, required=True, description='The count of cells per data type'),
    'data_distribution': fields.Nested(data_distribution_metadata, required=False, description='The distribution of the data in this column'),
    'consistency': fields.Nested(quality_dimension, required=False, description='The consistency quality score'),
    'redundancy': fields.Nested(quality_dimension, required=False, description='The redundancy quality score'),
    'variability': fields.Nested(quality_dimension, required=False, description='The variability quality score')
})
