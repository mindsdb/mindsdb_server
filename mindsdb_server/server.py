from flask import Flask, request
from flask_restplus import Resource, Api
from mindsdb_server.namespaces.predictor import ns_conf as predictor_ns
from mindsdb_server.namespaces.datasource import ns_conf as datasource_ns

app = Flask(__name__)
api = Api(app)

api.add_namespace(predictor_ns)
api.add_namespace(datasource_ns)

if __name__ == '__main__':
    app.run(debug=True)