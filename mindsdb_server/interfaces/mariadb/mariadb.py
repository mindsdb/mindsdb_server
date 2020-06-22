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
            DATA_SUBTYPES.SINGLE: 'Text',
            DATA_SUBTYPES.MULTIPLE: 'Text',
            DATA_SUBTYPES.IMAGE: 'Text',
            DATA_SUBTYPES.VIDEO: 'Text',
            DATA_SUBTYPES.AUDIO: 'Text',
            DATA_SUBTYPES.TEXT: 'Text',
            DATA_SUBTYPES.ARRAY: 'Text'
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

        msqyl_conn = self.config['api']['mysql']['host'] + ':' + str(self.config['api']['mysql']['port'])
        msqyl_user = self.config['api']['mysql']['user']
        msqyl_pass = self.config['api']['mysql']['password']

        if msqyl_pass is not None and mysql_pass != '':
            connect = f'mysql://{msqyl_user}@{self.host}/mindsdb/predictors_mariadb'
        else:
            connect = f'mysql://{msqyl_user}:{mysql_pass}@{self.host}/mindsdb/predictors_mariadb'

        q = f"""
                CREATE TABLE IF NOT EXISTS mindsdb.predictors
                (name Text,
                status Text,
                accuracy Text,
                predict_cols Text,
                select_data_query Text,
                training_options Text
                ) ENGINE=CONNECT TABLE_TYPE=MYSQL CONNECTION='{connect}';
        """
        print(f'Executing table creation query to create predictors list:\n{q}\n')
        self._query(q)

        q = f"""
            CREATE TABLE IF NOT EXISTS mindsdb.predictors (
                command Text
            ) ENGINE=CONNECT TABLE_TYPE=MYSQL CONNECTION='{connect}';
        """
        print(f'Executing table creation query to create command table:\n{q}\n')
        self._query(q)

    def register_predictor(self, name, stats):
        columns_sql = ','.join(self._to_mariadb_table(stats))
        columns_sql += ',`$select_data_query` Nullable(String)'

        msqyl_conn = self.config['api']['mysql']['host'] + ':' + str(self.config['api']['mysql']['port'])
        msqyl_user = self.config['api']['mysql']['user']
        msqyl_pass = self.config['api']['mysql']['password']

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
