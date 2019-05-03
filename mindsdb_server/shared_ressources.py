from flask import Flask
from flask_restplus import Api
import json

initialized = False
app = None
api = None


def get_shared():
    global initialized
    global app
    global api
    if initialized is False:
        print('Initializing shared ressources !')
        initialized = True
        app = Flask(__name__)
        api = Api(app)
        @app.route('/util/ping')
        def ping():
            return json.dumps({'status': 'ok'})
            
    return app, api
