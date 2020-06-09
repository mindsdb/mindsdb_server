import requests
from mindsdb.libs.constants.mindsdb import DATA_TYPES, DATA_SUBTYPES


class Clickhouse():
    def __init__(self, config):
        self.config = config
        self.host = config['interface']['clickhouse']['host']
        self.port = config['interface']['clickhouse']['port']
        self.user = config['interface']['clickhouse']['user']
        self.password = config['interface']['clickhouse']['password']

        self.create_predictors_table()


    def _to_clickhouse_table(self, stats):
        subtype_map = {
            DATA_SUBTYPES.INT: 'Int64',
            DATA_SUBTYPES.FLOAT: 'Float64',
            DATA_SUBTYPES.BINARY: 'UInt8',
            DATA_SUBTYPES.DATE: 'Date',
            DATA_SUBTYPES.TIMESTAMP: 'Datetime',
            DATA_SUBTYPES.SINGLE: 'String',
            DATA_SUBTYPES.MULTIPLE: 'String',
            DATA_SUBTYPES.IMAGE: 'String',
            DATA_SUBTYPES.VIDEO: 'String',
            DATA_SUBTYPES.AUDIO: 'String',
            DATA_SUBTYPES.TEXT: 'String',
            DATA_SUBTYPES.ARRAY: 'Array(Float64)'
        }

        column_declaration = []
        for name, column in stats.items():
            try:
                col_subtype = stats[name]['typing']['data_subtype']
                new_type = subtype_map[col_subtype]
                column_declaration.append(f' {name} {col_subtype} ')
            except Exception as e:
                print(e)
                print(f'Error: cant convert type {col_subtype} of column {name} to clickhouse tpye')

        return column_declaration

    def _query(self, query):
        params = {'user': 'default'}
        try:
            params['user'] = self.config['interface']['clickhouse']['user']
        except:
            pass

        try:
            params['password'] = self.config['interface']['clickhouse']['password']
        except:
            pass

        host = self.config['interface']['clickhouse']['host']
        port = self.config['interface']['clickhouse']['port']

        response = requests.post(f'http://{host}:{port}', data=query, params=params)

        return response

    def create_predictors_table(self):
        self._query('CREATE DATABASE IF NOT EXISTS mindsdb')

        msqyl_conn =  self.config['api']['mysql']['host'] + ':' + str(self.config['api']['mysql']['port'])
        msqyl_user =  self.config['api']['mysql']['user']
        msqyl_pass =  self.config['api']['mysql']['password']

        q = f"""
                CREATE TABLE IF NOT EXISTS mindsdb.predictors
                (name String,
                predict_cols String,
                select_data_query String,
                training_options String
                ) ENGINE=MySQL('{msqyl_conn}', 'mindsdb', 'predictors', '{msqyl_user}', '{msqyl_pass}')
        """
        print(f'Executing table creation query to create predictors list:\n{q}\n')
        self._query(q)


    def register_predictor(self, name, stats):
        columns_sql = '\n'.join(self._to_clickhouse_table(stats))

        msqyl_conn =  self.config['api']['mysql']['host'] + ':' + str(self.config['api']['mysql']['port'])
        msqyl_user =  self.config['api']['mysql']['user']
        msqyl_pass =  self.config['api']['mysql']['password']

        q = f"""
                CREATE TABLE mindsdb.{name}
                ({columns_sql}
                ) ENGINE=MySQL('{msqyl_conn}', 'mindsdb', '{name}', '{msqyl_user}', '{msqyl_pass}')
        """
        print(f'Executing table creation query to sync predictor:\n{q}\n')
        self._query(q)
