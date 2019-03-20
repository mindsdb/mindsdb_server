from flask_restplus import Namespace, Resource, fields

ns_conf = Namespace('predictors', description='Predictor is the main object exposed by the API')

predictor = ns_conf.model('Predictor', {
    'name': fields.String(required=True, description='The predictoe name'),
})

PREDICTORS = [
    {'name': 'Test'},
]

@ns_conf.route('/')
class PredictorList(Resource):
    @ns_conf.doc('list_predictors')
    @ns_conf.marshal_list_with(predictor)
    def get(self):
        '''List all predictors'''
        return PREDICTORS

@ns_conf.route('/<name>')
@ns_conf.param('name', 'The predictor identifier')
#@api.response(404, 'Cat not found')
class Predictor(Resource):
    @ns_conf.doc('get_predictor')
    @ns_conf.marshal_with(predictor)
    def get(self, id):
        '''Fetch a cat given its identifier'''
        for cat in PREDICTORS:
            if cat['id'] == id:
                return cat
        ns_conf.abort(404)