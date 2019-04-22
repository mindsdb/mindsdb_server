from mindsdb_server.namespaces.configs.predictors import ns_conf

from flask_restplus import fields


histogram_data = ns_conf.model('HistogramData', {
    'type': fields.String(required=True, description='The type of histogram', enum=['categorical', 'numeric']),
    'x': fields.List(fields.String, required=True, description='Ordered labels'),
    #'y': fields.List(fields.Float, required=True, description='Count for each label')
    'y': fields.List(fields.Raw, required=True, description='Count for each label')

})


NUMERIC_EXAMPLE = {
    'type': 'numeric',
    'x': ['1000','1100','1200','1300','1400','1500','1600','1700','1800','1900','2000','2100', '2200', '2300', '2400'],
    'y': [10,20,30,20,20,50,60,70,100,10,100,120,130,150,90]
}
