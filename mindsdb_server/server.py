from mindsdb_server.namespaces.predictor import ns_conf as predictor_ns
from mindsdb_server.namespaces.datasource import ns_conf as datasource_ns
from mindsdb_server.shared_ressources import get_shared
import json

app, api = get_shared()

api.add_namespace(predictor_ns)
api.add_namespace(datasource_ns)


if __name__ == '__main__':
    app.run(debug=True)
