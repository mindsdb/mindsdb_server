from flask import Flask, url_for
from flask_restplus import Api
import json
#from werkzeug.middleware.proxy_fix import ProxyFix


initialized = False
app = None
api = None

class Swagger_Api(Api):
    """
    This is a modification of the base Flask Restplus Api class due to the issue described here
    https://github.com/noirbizarre/flask-restplus/issues/223
    """

    @property
    def specs_url(self):
        return url_for(self.endpoint("specs"), _external=False)

def get_shared():
    global initialized
    global app
    global api
    if initialized is False:
        print('Initializing shared ressources !')
        initialized = True
        app = Flask(__name__)

        #app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)
        app.config['SWAGGER_HOST'] = 'http://localhost:8000/mindsdb_server'
        authorizations = {
            'apikey': {
                'type': 'apiKey',
                'in': 'query',
                'name': 'apikey'
            }
        }

        api = Swagger_Api(app, authorizations=authorizations, security=['apikey'], url_prefix=':8000')

    return app, api
