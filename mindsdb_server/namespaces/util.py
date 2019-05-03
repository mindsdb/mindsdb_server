from flask_restplus import Resource
from mindsdb_server.namespaces.configs.predictors import ns_conf
import json


@ns_conf.route('/')
class Ping(Resource):
    def get(self):
        print('HERE !')
        return json.dumps({'status': 'ok'})
