from flask_restplus import fields
from collections import OrderedDict
import datetime

from mindsdb_server.namespaces.configs.datasources import ns_conf

datasource_column_metadata = ns_conf.model('DatasourceColumnMetadata', {
    'name': fields.String(required=True, description='The datasource name'),
    'type': fields.String(required=True, description='column data type', enum=['string', 'number', 'file', 'dict']),
    'file_type': fields.String(required=False, description='type of files (if column type is "file")', enum=['image', 'sound']),
    'dict': fields.List(fields.String, required=False, description='dict keys (if column type is "dict")')
})

datasource_metadata = ns_conf.model('DatasourceMetadata', {
    # Primary key
    'name': fields.String(required=True, description='The datasource name'),
    # other attributes
    'source': fields.String(required=True, description='The datasource source (filename, url)'),
    'missed_files': fields.Boolean(required=True, description='indicates the presence of missed files'),
    'created_at': fields.DateTime(required=True, description='The time the datasource was created at'),
    'updated_at': fields.DateTime(required=True, description='The time the datasource was last updated at'),
    'row_count': fields.Integer(required=True, description='The number of rows in dataset'),
    'columns': fields.List(fields.Nested(datasource_column_metadata), required=True, description='columns description')
})

post_datasource_params = OrderedDict([
    ('name', {
        'description': 'The datasource name',
        'type': 'string',
        'in': 'path',
        'required': True
    })
])

put_datasource_params = OrderedDict([
    ('name', {
        'description': 'The datasource name',
        'type': 'string',
        'in': 'path',
        'required': True
    }),
    ('sourceType', {
        'description': 'type of datasource',
        'type': 'string',
        'enum': ['file','url'],
        'in': 'FormData',
        'required': True
    }),
    ('source', {
        'description': 'file name or url',
        'type': 'string',
        'in': 'FormData',
        'required': True
    }),
    ('file', {
        'description': 'datasource file',
        'type': 'file',
        'in': 'FormData',
        'required': False
    }),
    ('hashes', {
        'description': 'list of files hashes (if datasource has column with files)',
        'type': 'list',
        'in': 'FormData',
        'required': False
    })
])

EXAMPLES = [{
    'name': 'realty price',
    'source': 'data_sumple.csv',
    'missed_files': False,
    'created_at': datetime.datetime.now(),
    'updated_at': datetime.datetime.now(),
    'row_count': 3210,
    'columns': [{
        'name': 'name',
        'type': 'string'
    }, {
        'name': 'price',
        'type': 'number'
    }, {
        'name': 'rooms count',
        'type': 'number'
    }, {
        'name': 'photo',
        'type': 'file',
        'file_type': 'image'
    }, {
        'name': 'street',
        'type': 'dict',
        'dict': ['east', 'west']
    }]
}]
