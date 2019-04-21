from mindsdb_server.namespaces.configs.predictors import ns_conf
from mindsdb_server.namespaces.entitites.column_metadata import column_metadata

from flask_restplus import fields

nested_histogram_data = ns_conf.model('NestedHistogramData', {
    'x': fields.List(fields.String, required=True, description='Ordered labels'),
    #'y': fields.List(fields.Float, required=True, description='Count for each label'),
    'y': fields.List(fields.Raw, required=True, description='Count for each label'),
    'x_explained': fields.List(fields.List( fields.Nested(column_metadata)), required=True, description='Ordered list of lists where each element in the histogram has a list of column metadata only relevant to each  subset of data defined by the histogram bucket '),

})
