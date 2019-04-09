from flask import Flask, request
from flask_restplus import Resource, Api
from mindsdb_server.namespaces.predictor import ns_conf as predictor_ns

app = Flask(__name__)
api = Api(app)

api.add_namespace(predictor_ns)

if __name__ == '__main__':
    app.run(debug=True)