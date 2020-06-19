import pandas

from mindsdb_server.api.mysql.mysql_proxy.datahub.datanodes.datanode import DataNode
from mindsdb_server.interfaces.native.mindsdb import MindsdbNative
from mindsdb_server.interfaces.clickhouse.clickhouse import Clickhouse

class MindsDBDataNode(DataNode):
    type = 'mindsdb'

    def __init__(self, config):
        self.config = config
        self.mindsdb_native = MindsdbNative(config)

    def getTables(self):
        models = self.mindsdb_native.get_models()
        models = [x['name'] for x in models if x['status'] == 'complete']
        models += ['predictors']
        return models

    def hasTable(self, table):
        return table in self.getTables()

    def getTableColumns(self, table):
        if table == 'predictors':
            return ['name', 'status', 'accuracy', 'predict_cols', 'select_data_query', 'training_options']
        model = self.mindsdb_native.get_model_data(name=table)
        columns = []
        columns += [x['column_name'] for x in model['data_analysis']['input_columns_metadata']]
        columns += [x['column_name'] for x in model['data_analysis']['target_columns_metadata']]
        # TODO this should be added just for clickhouse queries
        columns += ['$clickhouse_data_query']
        return columns

    def _select_predictors(self):
        models = self.mindsdb_native.get_models()
        return [{
            'name': x['name'],
            'status': x['status'],
            'accuracy': x['accuracy'],
            'predict_cols': ', '.join(x['predict']),
            'select_data_query': x['data_source'],
            'training_options': ''  # TODEL ?
        } for x in models]

    def delete_predictor(self, name):
        self.mindsdb_native.delete_model(name)

    def select(self, table, columns=None, where=None, where_data=None, order_by=None, group_by=None):
        if table == 'predictors':
            return self._select_predictors()

        if '$clickhouse_data_query' in where:
            clickhouse_query = where['$clickhouse_data_query']['$eq']
            del where['$clickhouse_data_query']
            ch = Clickhouse(self.config)
            res = ch._query(clickhouse_query.strip(' ;') + ' FORMAT JSON')
            data = res.json()['data']
            if where_data is None:
                where_data = data
            else:
                where_data += data

        # NOTE WHERE statements can be just $eq joined with 'and'
        new_where = {}
        for key, value in where.items():
            if isinstance(value, dict) is False or len(value.keys()) != 1 or list(value.keys())[0] != '$eq':
                # TODO value should be just string or number
                raise Exception()
            new_where[key] = value['$eq']
        if len(new_where) == 0:
            new_where = None

        if where_data is not None:
            where_data = pandas.DataFrame(where_data)

        res = self.mindsdb_native.predict(name=table, when=new_where, when_data=where_data)

        predicted_columns = self.mindsdb_native.get_model_data(name=table)['predict']
        length = len(res.data[predicted_columns[0]])

        data = []
        keys = [x for x in list(res.data.keys()) if x in columns]
        for i in range(length):
            row = {}
            for key in keys:
                row[key] = res.data[key][i]
            data.append(row)

        if clickhouse_query is not None:
            for row in data:
                row['$clickhouse_data_query'] = clickhouse_query

        if new_where is not None and len(new_where.keys()) > 0:
            columns = self.getTableColumns(table)
            for row in data:
                for column in columns:
                    if column not in row:
                        row[column] = None
                row.update(new_where)

        return data
