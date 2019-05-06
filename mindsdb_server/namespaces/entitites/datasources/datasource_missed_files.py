from flask_restplus import fields
from collections import OrderedDict

from mindsdb_server.namespaces.configs.datasources import ns_conf

get_datasource_missed_files_params = OrderedDict([
    ('page[size]', {
        'description': 'page size',
        'type': 'integer',
        'in': 'path',
        'required': False,
        'default': 0
    }),
    ('page[number]', {
        'description': 'start page',
        'type': 'integer',
        'in': 'path',
        'required': False,
        'default': 0
    })
])

datasource_missed_file_metadata = ns_conf.model('DatasourceMissedFile', {
    'column_name': fields.String(required=True, description='file column name'),
    'index': fields.Integer(required=True, description='row index in datasource'),
    'path': fields.String(required=True, description='file column value')
})

datasource_missed_files_metadata = ns_conf.model('DatasourceMissedFiles', {
    'rowcount': fields.Integer(required=True, description='number of missed files'),
    'data': fields.List(fields.Nested(datasource_missed_file_metadata), required=True, description='columns description')
})

EXAMPLES = [{
    'rowcount': 2,
    'data': [{
        'column_name': 'file',
        'index': 3,
        'path': '/tmp/3.jpg'
    }, {
        'column_name': 'file',
        'index': 4,
        'path': '/tmp/4.jpg'
    }]
}]
