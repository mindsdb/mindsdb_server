from mindsdb_server.namespaces.configs.predictors import ns_conf
from flask_restplus import fields

label_group = ns_conf.model('LabelGroup', {
    'group': fields.String(required=True, description='label name'),
    'members': fields.List(fields.String, required=False, description='members belonging to this group'),
})
