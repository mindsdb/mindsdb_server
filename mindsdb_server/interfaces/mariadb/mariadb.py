import requests

import mysql.connector

from mindsdb.libs.constants.mindsdb import DATA_TYPES, DATA_SUBTYPES


class Mariadb():
    def __init__(self, config):
        self.config = config
        self.host = config['integrations']['mariadb']['host']
        self.port = config['integrations']['mariadb']['port']
        self.user = config['integrations']['mariadb']['user']
        self.password = config['integrations']['mariadb']['password']

        self.setup_mariadb()


    def _to_mariadb_table(self, stats):
        subtype_map = {
            DATA_SUBTYPES.INT: 'Int64',
            DATA_SUBTYPES.FLOAT: 'Float64',
            DATA_SUBTYPES.BINARY: 'UInt8',
            DATA_SUBTYPES.DATE: 'Date',
            DATA_SUBTYPES.TIMESTAMP: 'Datetime',
            DATA_SUBTYPES.SINGLE: 'VARCHAR(500)',
            DATA_SUBTYPES.MULTIPLE: 'VARCHAR(500)',
            DATA_SUBTYPES.IMAGE: 'VARCHAR(500)',
            DATA_SUBTYPES.VIDEO: 'VARCHAR(500)',
            DATA_SUBTYPES.AUDIO: 'VARCHAR(500)',
            DATA_SUBTYPES.TEXT: 'VARCHAR(500)',
            DATA_SUBTYPES.ARRAY: 'VARCHAR(500)'
        }

        column_declaration = []
        for name, column in stats.items():
            try:
                col_subtype = stats[name]['typing']['data_subtype']
                new_type = subtype_map[col_subtype]
                column_declaration.append(f' `{name}` {new_type} ')
            except Exception as e:
                print(e)
                print(f'Error: cant convert type {col_subtype} of column {name} to mariadb tpye')

        return column_declaration

    def _query(self, query):
        con = mysql.connector.connect(host=self.host, port=self.port, user=self.user, password=self.password)

        cur = con.cursor()
        cur.execute(query)
        con.commit()
        con.close()

        return True

    def setup_mariadb(self):
        self._query('CREATE DATABASE IF NOT EXISTS mindsdb')

        user = self.user
        password = self.password
        host = self.host

        if password is None or password == '':
            connect = f'mysql://{user}@{host}/mindsdb/predictors_mariadb'
        else:
            connect = f'mysql://{user}:{password}@{host}/mindsdb/predictors_mariadb'

        q = f"""
                CREATE TABLE IF NOT EXISTS mindsdb.predictors
                (name VARCHAR(500),
                status VARCHAR(500),
                accuracy VARCHAR(500),
                predict_cols VARCHAR(500),
                select_data_query VARCHAR(500),
                training_options VARCHAR(500)
                ) ENGINE=CONNECT TABLE_TYPE=MYSQL CONNECTION='{connect}';
        """
        print(f'Executing table creation query to create predictors list:\n{q}\n')
        self._query(q)

        q = f"""
            CREATE TABLE IF NOT EXISTS mindsdb.predictors (
                command VARCHAR(500)
            ) ENGINE=CONNECT TABLE_TYPE=MYSQL CONNECTION='{connect}';
        """
        print(f'Executing table creation query to create command table:\n{q}\n')
        self._query(q)

    def register_predictor(self, name, stats):
        columns_sql = ','.join(self._to_mariadb_table(stats))
        columns_sql += ',`$select_data_query` Nullable(String)'

        mariadb_conn = self.config['api']['mysql']['host'] + ':' + str(self.config['api']['mysql']['port'])
        mariadb_user = self.config['api']['mysql']['user']
        mariadb_pass = self.config['api']['mysql']['password']

        q = f"""
                CREATE TABLE mindsdb.{name}
                ({columns_sql}
                ) ENGINE=CONNECT TABLE_TYPE=MYSQL CONNECTION='{connect}';
        """
        print(f'Executing table creation query to sync predictor:\n{q}\n')
        self._query(q)

    def unregister_predictor(self, name):
        q = f"""
            drop table if exists mindsdb.{name};
        """
        print(f'Executing table creation query to sync predictor:\n{q}\n')
        self._query(q)
