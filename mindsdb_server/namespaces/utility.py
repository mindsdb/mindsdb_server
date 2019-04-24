from flask_restplus import Resource, fields
from mindsdb_server.namespaces.configs.utilities import ns_conf


@ns_conf.route('/ping')
class Ping(Resource):
    @ns_conf.doc('get_ping')
    def get(self):
        '''Checks server avaliable'''
        return 'pong'
