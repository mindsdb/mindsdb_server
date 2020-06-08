import pandas
import ray
import mindsdb

from mindsdb_server.api.mysql.mysql_proxy.datasources.datasource import DataSource
from mindsdb_server.interfaces.native.native import get_models

@ray.remote
class MindsDBDataSource(DataSource):
    type = 'mindsdb'

    def __init__(self):
        self.mindsdb_native = MindsdbNative({})

    def getTables(self):
        models = self.mindsdb_native.get_models()
        models = [x['name'] for x in models if x['status'] == 'complete']
        return models

    def hasTable(self, table):
        return table in getTables()

    def getTableColumns(self, table):
        model = mindsdb.Predictor(name=table).get_model_data()
        columns = []
        columns += [x['column_name'] for x in model['data_analysis']['input_columns_metadata']]
        columns += [x['column_name'] for x in model['data_analysis']['target_columns_metadata']]
        return columns

    def select(self, table, columns=None, where=None, where_data=None, order_by=None, group_by=None):
        # NOTE WHERE statements can be just $eq joined with 'and'
        new_where = {}
        for key, value in where.items():
            if isinstance(value, dict) is False or len(value.keys()) != 1 or list(value.keys())[0] != '$eq':
                # TODO value should be just string or number
                raise Exception()
            new_where[key] = value['$eq']
        p = mindsdb.Predictor(name=table)

        if where_data is not None:
            where_data = pandas.DataFrame(where_data)
        res = p.predict(when=new_where, when_data=where_data, use_gpu=False)

        predicted_columns = p.get_model_data()['predict']
        length = len(res.data[predicted_columns[0]])
        data = []
        # keys = [x for x in list(res.data.keys()) if x in columns and x in predicted_columns]
        keys = [x for x in list(res.data.keys()) if x in columns]
        for i in range(length):
            row = {}
            for key in keys:
                row[key] = res.data[key][i]
            data.append(row)

        if len(new_where.keys()) > 0:
            columns = self.getTableColumns(table)
            for row in data:
                for column in columns:
                    if column not in row:
                        row[column] = None
                row.update(new_where)

        return data
