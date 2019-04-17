from collections import OrderedDict
from flask_restplus import fields
from mindsdb_server.namespaces.configs.datasources import ns_conf

get_datasource_rows_params = OrderedDict([
    ('page[size]', {
        'description': 'page size',
        'type': 'integer',
        'in': 'path',
        'required': False,
        'default': 10
    }),
    ('page[number]', {
        'description': 'start page',
        'type': 'integer',
        'in': 'path',
        'required': False,
        'default': 0
    })
])

datasource_rows_metadata = ns_conf.model('RowsResponse', {
    'data': fields.List(fields.Raw, required=True, description='rows of datasource data')
})

EXAMPLES = [{
    'data': [
        {
            'name': 'Mercury',
            'mass': 0.055,
            'radius': 0.3829
        }, {
            'name': 'Venus',
            'mass': 0.815,
            'radius': 0.9499
        }, {
            'name': 'Earth',
            'mass': 1.0,
            'radius': 1.0
        }
    ]
}]
